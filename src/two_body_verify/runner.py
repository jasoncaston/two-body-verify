"""Project verification orchestration."""

from pathlib import Path
from typing import Dict, List

from .checks import run_check
from .claims import load_claims
from .models import ClaimResult, VerificationReport


PILLAR_ORDER = ("artifact", "tests", "sources", "docs")


def _claim_status(statuses: List[str]) -> str:
    if "contradicted" in statuses:
        return "contradicted"
    if "unsupported" in statuses:
        return "unsupported"
    return "evidenced"


def verify_project(project: Path, claims_file: Path) -> VerificationReport:
    project = project.resolve()
    if not project.is_dir():
        raise ValueError(f"project path is not a directory: {project}")
    claims = load_claims(claims_file.resolve())
    results: List[ClaimResult] = []
    pillar_results: Dict[str, List[bool]] = {pillar: [] for pillar in PILLAR_ORDER}
    for claim in claims:
        checks = [run_check(project, spec) for spec in claim["checks"]]
        for check in checks:
            pillar_results[check.pillar].append(check.status == "evidenced")
        results.append(
            ClaimResult(
                claim_id=claim["id"],
                statement=claim["statement"],
                status=_claim_status([check.status for check in checks]),
                checks=checks,
            )
        )
    pillar_scores = {
        pillar: (5 * sum(values)) // len(values) if values else 0
        for pillar, values in pillar_results.items()
    }
    return VerificationReport(
        project=str(project),
        score=sum(pillar_scores.values()),
        score_max=20,
        pillar_scores=pillar_scores,
        claims=results,
    )
