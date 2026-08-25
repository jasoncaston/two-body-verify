"""Concrete checks used by the verification runner."""

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .models import CheckResult, Finding


PILLARS = {
    "file_content": "artifact",
    "pdf_visible_text": "artifact",
    "csv_formula_safe": "artifact",
    "name_length_cap": "artifact",
    "test_asserts_values": "tests",
    "external_source": "sources",
    "documented_feature_invoked": "docs",
    "suite_claim_evidence": "tests",
}


def _result(
    kind: str,
    status: str,
    facts: Dict[str, Any],
    findings: Iterable[Finding] = (),
) -> CheckResult:
    return CheckResult(kind, PILLARS[kind], status, facts, list(findings))


def _project_file(project: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute():
        raise ValueError("check paths must be non-empty and relative")
    candidate = (project / relative).resolve()
    try:
        candidate.relative_to(project.resolve())
    except ValueError as exc:
        raise ValueError(f"check path escapes project: {relative}") from exc
    return candidate


def _read_text(project: Path, relative: str) -> str:
    return _project_file(project, relative).read_text(encoding="utf-8")


def check_file_content(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "file_content"
    relative = spec.get("path", "")
    required = spec.get("contains", [])
    path = _project_file(project, relative)
    facts = {"path": relative, "exists": path.is_file(), "required": required}
    if not path.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("artifact-missing", "The claimed artifact does not exist.", relative)],
        )
    if not required:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("file-content-not-checked", "File existence alone does not verify its content.", relative)],
        )
    text = path.read_text(encoding="utf-8")
    missing = [value for value in required if value not in text]
    facts.update({"characters_read": len(text), "missing": missing})
    if missing:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("artifact-content-contradiction", "The artifact is missing claimed content.", relative)],
        )
    return _result(kind, "evidenced", facts)


def check_pdf_visible_text(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "pdf_visible_text"
    pdf_path = spec.get("path", "")
    rendered_path = spec.get("rendered_text_path", "")
    expected = spec.get("contains", [])
    pdf = _project_file(project, pdf_path)
    facts = {
        "path": pdf_path,
        "pdf_exists": pdf.is_file(),
        "rendered_text_path": rendered_path,
        "expected": expected,
    }
    if not pdf.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("artifact-missing", "The claimed PDF does not exist.", pdf_path)],
        )
    if not rendered_path or not expected:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("pdf-visible-text-unverified", "PDF metadata does not verify visible rendered text.", pdf_path)],
        )
    rendered = _project_file(project, rendered_path)
    if not rendered.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("pdf-visible-text-unverified", "No rendered text evidence was found for the PDF.", rendered_path)],
        )
    visible_text = rendered.read_text(encoding="utf-8")
    missing = [value for value in expected if value not in visible_text]
    facts.update({"visible_characters_read": len(visible_text), "missing": missing})
    if missing:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("pdf-visible-text-contradiction", "Rendered PDF text is missing claimed content.", rendered_path)],
        )
    return _result(kind, "evidenced", facts)


def check_csv_formula_safe(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "csv_formula_safe"
    relative = spec.get("path", "")
    path = _project_file(project, relative)
    facts: Dict[str, Any] = {"path": relative, "exists": path.is_file(), "unsafe_cells": []}
    if not path.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("artifact-missing", "The claimed CSV does not exist.", relative)],
        )
    unsafe: List[Dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row_number, row in enumerate(csv.reader(handle), start=1):
            for column_number, value in enumerate(row, start=1):
                normalized = value.lstrip("\r\n")
                if normalized.startswith(("=", "+", "-", "@")):
                    unsafe.append(
                        {
                            "row": row_number,
                            "column": column_number,
                            "leading_newline": value.startswith(("\r", "\n")),
                        }
                    )
    facts["unsafe_cells"] = unsafe
    if unsafe:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("csv-formula-injection", "The CSV contains a formula-shaped cell.", relative)],
        )
    return _result(kind, "evidenced", facts)


def _named_values(value: Any, location: str = "$") -> Iterable[tuple]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "name" and isinstance(child, str):
                yield child_location, child
            yield from _named_values(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _named_values(child, f"{location}[{index}]")


def check_name_length_cap(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "name_length_cap"
    relative = spec.get("path", "")
    maximum = spec.get("max_length", 64)
    if not isinstance(maximum, int) or maximum < 1:
        raise ValueError("max_length must be a positive integer")
    path = _project_file(project, relative)
    facts: Dict[str, Any] = {"path": relative, "max_length": maximum, "violations": []}
    if not path.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("artifact-missing", "The manifest or config does not exist.", relative)],
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    violations = [
        {"location": location, "length": len(value)}
        for location, value in _named_values(data)
        if len(value) > maximum
    ]
    facts["violations"] = violations
    if violations:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("name-length-cap-exceeded", "A manifest or config name exceeds its cap.", relative)],
        )
    return _result(kind, "evidenced", facts)


def check_test_asserts_values(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "test_asserts_values"
    relative = spec.get("path", "")
    expected = spec.get("expected_tokens", [])
    path = _project_file(project, relative)
    facts: Dict[str, Any] = {"path": relative, "expected_tokens": expected, "exists": path.is_file()}
    if not path.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("test-evidence-missing", "The claimed test file does not exist.", relative)],
        )
    text = path.read_text(encoding="utf-8")
    assertions = re.findall(r"(?m)^\s*assert\s+(.+)$", text)
    facts["assertion_count"] = len(assertions)
    if not assertions:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("test-has-no-assertion", "The test file contains no assertion.", relative)],
        )
    assertion_text = "\n".join(assertions)
    content_read = any(token in text for token in ("read_text(", "read_bytes(", "json.load", "csv.reader", ".text"))
    existence_only = any(token in assertion_text for token in (".exists()", ".is_file()", "st_size", "getsize("))
    real_values = bool(expected) and all(token in assertion_text for token in expected)
    facts.update(
        {
            "content_read": content_read,
            "existence_or_size_asserted": existence_only,
            "expected_values_asserted": real_values,
        }
    )
    if existence_only and not content_read:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("file-content-not-asserted", "The test checks file existence or size without checking content.", relative)],
        )
    exit_only = any(token in assertion_text for token in ("returncode", "exit_code", "SystemExit")) and not real_values
    facts["exit_code_only"] = exit_only
    if exit_only:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("exit-code-only-test", "The test checks an exit code without asserting the claimed value.", relative)],
        )
    if not real_values:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("real-value-not-asserted", "The test does not assert every required value.", relative)],
        )
    return _result(kind, "evidenced", facts)


def check_external_source(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "external_source"
    relative = spec.get("path", "")
    source = spec.get("source", "")
    path = _project_file(project, relative)
    facts = {"path": relative, "source": source, "exists": path.is_file()}
    if not source or not re.match(r"^https?://", source):
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("external-claim-untraced", "The external claim has no traceable source URL.", relative)],
        )
    if not path.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("source-record-missing", "The source record does not exist.", relative)],
        )
    recorded = source in path.read_text(encoding="utf-8")
    facts["source_recorded"] = recorded
    if not recorded:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("source-record-contradiction", "The named source is not recorded in the source artifact.", relative)],
        )
    return _result(kind, "evidenced", facts)


def check_documented_feature_invoked(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "documented_feature_invoked"
    docs_path = spec.get("docs_path", "")
    implementation_path = spec.get("implementation_path", "")
    invocation_path = spec.get("invocation_path", "")
    docs_marker = spec.get("docs_token", "")
    implementation_marker = spec.get("implementation_token", "")
    invocation_marker = spec.get("invocation_token", "")
    facts = {
        "docs_path": docs_path,
        "implementation_path": implementation_path,
        "invocation_path": invocation_path,
        "documented": False,
        "implemented": False,
        "invoked": False,
    }
    required_paths = [docs_path, implementation_path, invocation_path]
    if not all(required_paths) or not all((docs_marker, implementation_marker, invocation_marker)):
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("feature-evidence-incomplete", "The documented feature check is missing a path or value.")],
        )
    try:
        docs = _read_text(project, docs_path)
        implementation = _read_text(project, implementation_path)
    except FileNotFoundError:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("feature-artifact-missing", "A documented feature artifact does not exist.")],
        )
    facts["documented"] = docs_marker in docs
    facts["implemented"] = implementation_marker in implementation
    invocation = _project_file(project, invocation_path)
    if invocation.is_file():
        facts["invoked"] = invocation_marker in invocation.read_text(encoding="utf-8")
    if not facts["documented"]:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("docs-claim-missing", "The named feature is not present in the documentation.", docs_path)],
        )
    if not facts["implemented"]:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("documented-feature-not-implemented", "The documented feature is not present in the implementation.", implementation_path)],
        )
    if not facts["invoked"]:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("documented-feature-uninvoked", "The documented feature has not been invoked by the named evidence.", invocation_path)],
        )
    return _result(kind, "evidenced", facts)


def check_suite_claim_evidence(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = "suite_claim_evidence"
    suite_path = spec.get("suite_path", "")
    evidence_path = spec.get("evidence_path", "")
    expected = spec.get("expected_tokens", [])
    facts = {
        "suite_path": suite_path,
        "evidence_path": evidence_path,
        "expected_tokens": expected,
        "suite_passed": False,
        "claim_values_evidenced": False,
    }
    suite = _project_file(project, suite_path)
    if not suite.is_file():
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("suite-result-missing", "The test suite result does not exist.", suite_path)],
        )
    suite_text = suite.read_text(encoding="utf-8")
    facts["suite_passed"] = bool(re.search(r"\bpassed\b", suite_text, re.IGNORECASE))
    if evidence_path:
        evidence = _project_file(project, evidence_path)
        if evidence.is_file() and expected:
            evidence_text = evidence.read_text(encoding="utf-8")
            facts["claim_values_evidenced"] = all(token in evidence_text for token in expected)
    if facts["suite_passed"] and not facts["claim_values_evidenced"]:
        return _result(
            kind,
            "unsupported",
            facts,
            [Finding("suite-pass-not-claim-proof", "A passing suite does not verify the named claim by itself.", suite_path)],
        )
    if not facts["suite_passed"]:
        return _result(
            kind,
            "contradicted",
            facts,
            [Finding("suite-did-not-pass", "The recorded test suite did not pass.", suite_path)],
        )
    return _result(kind, "evidenced", facts)


CHECKERS = {
    "file_content": check_file_content,
    "pdf_visible_text": check_pdf_visible_text,
    "csv_formula_safe": check_csv_formula_safe,
    "name_length_cap": check_name_length_cap,
    "test_asserts_values": check_test_asserts_values,
    "external_source": check_external_source,
    "documented_feature_invoked": check_documented_feature_invoked,
    "suite_claim_evidence": check_suite_claim_evidence,
}


def run_check(project: Path, spec: Dict[str, Any]) -> CheckResult:
    kind = spec.get("kind", "")
    if kind not in CHECKERS:
        raise ValueError(f"unknown check kind: {kind or '<missing>'}")
    return CHECKERS[kind](project, spec)
