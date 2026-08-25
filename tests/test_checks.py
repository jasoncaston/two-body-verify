from pathlib import Path

import pytest

from two_body_verify.checks import run_check


FIXTURES = Path(__file__).parent / "fixtures"
GOOD = FIXTURES / "good"
BAD = FIXTURES / "bad"


def finding_codes(result):
    return [finding.code for finding in result.findings]


def test_file_content_check_reads_required_value():
    result = run_check(
        GOOD,
        {"kind": "file_content", "path": "artifact.txt", "contains": ["release status: verified"]},
    )
    assert result.status == "evidenced"
    assert result.facts["characters_read"] == 25
    assert result.facts["missing"] == []


def test_file_existence_without_content_is_unsupported():
    result = run_check(BAD, {"kind": "file_content", "path": "artifact.txt"})
    assert result.status == "unsupported"
    assert result.facts["exists"] is True
    assert finding_codes(result) == ["file-content-not-checked"]


def test_test_assertion_reads_file_content():
    result = run_check(
        GOOD,
        {
            "kind": "test_asserts_values",
            "path": "test_content.py",
            "expected_tokens": ["release status: verified"],
        },
    )
    assert result.status == "evidenced"
    assert result.facts["content_read"] is True
    assert result.facts["expected_values_asserted"] is True


def test_test_assertion_on_existence_and_size_is_unsupported():
    result = run_check(
        BAD,
        {
            "kind": "test_asserts_values",
            "path": "test_exists_only.py",
            "expected_tokens": ["release status: verified"],
        },
    )
    assert result.status == "unsupported"
    assert result.facts["existence_or_size_asserted"] is True
    assert finding_codes(result) == ["file-content-not-asserted"]


def test_pdf_check_uses_visible_rendered_text():
    result = run_check(
        GOOD,
        {
            "kind": "pdf_visible_text",
            "path": "report.pdf",
            "rendered_text_path": "rendered.txt",
            "contains": ["Visible verification report"],
        },
    )
    assert result.status == "evidenced"
    assert result.facts["visible_characters_read"] == 28
    assert result.facts["missing"] == []


def test_pdf_metadata_without_rendered_text_is_unsupported():
    result = run_check(
        BAD,
        {"kind": "pdf_visible_text", "path": "report.pdf", "contains": ["Visible verification report"]},
    )
    assert result.status == "unsupported"
    assert result.facts["pdf_exists"] is True
    assert finding_codes(result) == ["pdf-visible-text-unverified"]


def test_csv_safe_values_have_no_formula_cells():
    result = run_check(GOOD, {"kind": "csv_formula_safe", "path": "safe.csv"})
    assert result.status == "evidenced"
    assert result.facts["unsafe_cells"] == []


def test_csv_leading_newline_formula_is_detected():
    result = run_check(BAD, {"kind": "csv_formula_safe", "path": "unsafe.csv"})
    assert result.status == "contradicted"
    assert result.facts["unsafe_cells"] == [{"row": 2, "column": 2, "leading_newline": True}]
    assert finding_codes(result) == ["csv-formula-injection"]


def test_manifest_names_within_cap_are_evidenced():
    result = run_check(GOOD, {"kind": "name_length_cap", "path": "manifest.json", "max_length": 16})
    assert result.status == "evidenced"
    assert result.facts["violations"] == []


def test_manifest_name_over_cap_is_contradicted():
    result = run_check(BAD, {"kind": "name_length_cap", "path": "manifest.json", "max_length": 10})
    assert result.status == "contradicted"
    assert result.facts["violations"] == [{"location": "$.name", "length": 51}]
    assert finding_codes(result) == ["name-length-cap-exceeded"]


def test_real_value_assertion_closes_test_check():
    result = run_check(
        GOOD,
        {"kind": "test_asserts_values", "path": "test_values.py", "expected_tokens": ["status", "verified"]},
    )
    assert result.status == "evidenced"
    assert result.facts["assertion_count"] == 2
    assert result.facts["exit_code_only"] is False


def test_exit_code_only_assertion_is_unsupported():
    result = run_check(
        BAD,
        {"kind": "test_asserts_values", "path": "test_exit_only.py", "expected_tokens": ["status", "verified"]},
    )
    assert result.status == "unsupported"
    assert result.facts["exit_code_only"] is True
    assert finding_codes(result) == ["exit-code-only-test"]


def test_documented_feature_with_invocation_is_evidenced():
    result = run_check(
        GOOD,
        {
            "kind": "documented_feature_invoked",
            "docs_path": "README.md",
            "docs_token": "export_report",
            "implementation_path": "feature.py",
            "implementation_token": "def export_report",
            "invocation_path": "test_feature.py",
            "invocation_token": "export_report(",
        },
    )
    assert result.status == "evidenced"
    assert result.facts["documented"] is True
    assert result.facts["implemented"] is True
    assert result.facts["invoked"] is True


def test_documented_feature_without_invocation_is_unsupported():
    result = run_check(
        BAD,
        {
            "kind": "documented_feature_invoked",
            "docs_path": "README.md",
            "docs_token": "export_report",
            "implementation_path": "feature.py",
            "implementation_token": "def export_report",
            "invocation_path": "test_feature.py",
            "invocation_token": "export_report(",
        },
    )
    assert result.status == "unsupported"
    assert result.facts["implemented"] is True
    assert result.facts["invoked"] is False
    assert finding_codes(result) == ["documented-feature-uninvoked"]


def test_suite_with_claim_evidence_is_evidenced():
    result = run_check(
        GOOD,
        {
            "kind": "suite_claim_evidence",
            "suite_path": "suite.log",
            "evidence_path": "claim-evidence.txt",
            "expected_tokens": ["release status: verified"],
        },
    )
    assert result.status == "evidenced"
    assert result.facts["suite_passed"] is True
    assert result.facts["claim_values_evidenced"] is True


def test_passing_suite_without_claim_evidence_is_unsupported():
    result = run_check(BAD, {"kind": "suite_claim_evidence", "suite_path": "suite.log"})
    assert result.status == "unsupported"
    assert result.facts["suite_passed"] is True
    assert result.facts["claim_values_evidenced"] is False
    assert finding_codes(result) == ["suite-pass-not-claim-proof"]


def test_external_claim_with_recorded_source_is_evidenced():
    result = run_check(
        GOOD,
        {"kind": "external_source", "path": "SOURCES.md", "source": "https://example.com/reference"},
    )
    assert result.status == "evidenced"
    assert result.facts["source_recorded"] is True


def test_external_claim_without_url_is_unsupported():
    result = run_check(BAD, {"kind": "external_source", "path": "SOURCES.md", "source": ""})
    assert result.status == "unsupported"
    assert result.facts["source"] == ""
    assert finding_codes(result) == ["external-claim-untraced"]


def test_unknown_check_kind_is_rejected():
    with pytest.raises(ValueError, match="unknown check kind: mystery"):
        run_check(GOOD, {"kind": "mystery"})
