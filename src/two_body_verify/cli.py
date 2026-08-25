"""Command line interface for two-body-verify."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .runner import PILLAR_ORDER, verify_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="two-body-verify",
        description="Verify delivery claims against project artifacts.",
    )
    parser.add_argument("project", type=Path, help="project directory to inspect")
    parser.add_argument("claims", type=Path, help="version 1 JSON claims file")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def render_report(report) -> str:
    lines = [f"Verification score: {report.score}/{report.score_max}"]
    lines.append(
        "Pillars: "
        + ", ".join(f"{pillar} {report.pillar_scores[pillar]}/5" for pillar in PILLAR_ORDER)
    )
    lines.append("")
    lines.append("STATUS        CLAIM                 FINDINGS")
    for claim in report.claims:
        findings = [finding for check in claim.checks for finding in check.findings]
        summary = "; ".join(finding.code for finding in findings) or "evidence matched"
        lines.append(f"{claim.status:<13} {claim.claim_id:<21} {summary}")
        for finding in findings:
            location = f" [{finding.path}]" if finding.path else ""
            lines.append(f"  {finding.code}{location}: {finding.message}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = verify_project(args.project, args.claims)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if all(claim.status == "evidenced" for claim in report.claims) else 1
