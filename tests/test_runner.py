import json
from pathlib import Path

from two_body_verify.runner import verify_project


FIXTURES = Path(__file__).parent / "fixtures"


def write_claims(tmp_path, claims):
    path = tmp_path / "claims.json"
    path.write_text(json.dumps({"version": 1, "claims": claims}), encoding="utf-8")
    return path


def test_full_report_scores_four_real_pillars():
    report = verify_project(FIXTURES / "good", FIXTURES / "good-claims.json")
    assert report.score == 20
    assert report.pillar_scores == {"artifact": 5, "tests": 5, "sources": 5, "docs": 5}
    assert report.claims[0].status == "evidenced"
    assert report.to_dict()["counts"] == {"evidenced": 1, "unsupported": 0, "contradicted": 0}


def test_claim_without_supporting_artifact_is_unsupported(tmp_path):
    claims = write_claims(
        tmp_path,
        [
            {
                "id": "missing-report",
                "statement": "A report was produced.",
                "checks": [{"kind": "file_content", "path": "missing.txt", "contains": ["verified"]}],
            }
        ],
    )
    report = verify_project(FIXTURES / "bad", claims)
    check = report.claims[0].checks[0]
    assert report.claims[0].status == "unsupported"
    assert check.facts["exists"] is False
    assert [finding.code for finding in check.findings] == ["artifact-missing"]


def test_claim_contradicted_by_artifact_is_contradicted(tmp_path):
    claims = write_claims(
        tmp_path,
        [
            {
                "id": "verified-report",
                "statement": "The report says verified.",
                "checks": [
                    {"kind": "file_content", "path": "artifact.txt", "contains": ["release status: verified"]}
                ],
            }
        ],
    )
    report = verify_project(FIXTURES / "bad", claims)
    check = report.claims[0].checks[0]
    assert report.claims[0].status == "contradicted"
    assert check.facts["missing"] == ["release status: verified"]
    assert [finding.code for finding in check.findings] == ["artifact-content-contradiction"]


def test_unchecked_pillars_score_zero(tmp_path):
    claims = write_claims(
        tmp_path,
        [
            {
                "id": "artifact-only",
                "statement": "The artifact has a verified status.",
                "checks": [
                    {"kind": "file_content", "path": "artifact.txt", "contains": ["release status: verified"]}
                ],
            }
        ],
    )
    report = verify_project(FIXTURES / "good", claims)
    assert report.score == 5
    assert report.pillar_scores == {"artifact": 5, "tests": 0, "sources": 0, "docs": 0}
