"""Data models for verification results."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    path: str = ""

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class CheckResult:
    kind: str
    pillar: str
    status: str
    facts: Dict[str, Any] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "pillar": self.pillar,
            "status": self.status,
            "facts": self.facts,
            "findings": [item.to_dict() for item in self.findings],
        }


@dataclass
class ClaimResult:
    claim_id: str
    statement: str
    status: str
    checks: List[CheckResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.claim_id,
            "statement": self.statement,
            "status": self.status,
            "checks": [item.to_dict() for item in self.checks],
        }


@dataclass
class VerificationReport:
    project: str
    score: int
    score_max: int
    pillar_scores: Dict[str, int]
    claims: List[ClaimResult]

    def to_dict(self) -> Dict[str, Any]:
        counts = {name: 0 for name in ("evidenced", "unsupported", "contradicted")}
        for claim in self.claims:
            counts[claim.status] += 1
        return {
            "project": self.project,
            "score": self.score,
            "score_max": self.score_max,
            "pillar_scores": self.pillar_scores,
            "counts": counts,
            "claims": [item.to_dict() for item in self.claims],
        }
