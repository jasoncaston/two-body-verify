import json
from pathlib import Path

from two_body_verify.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def test_default_report_contains_status_score_and_claim(capsys):
    exit_code = main([str(FIXTURES / "good"), str(FIXTURES / "good-claims.json")])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Verification score: 20/20" in output
    assert "evidenced     complete-report" in output
    assert "artifact 5/5" in output


def test_json_report_contains_parsed_values(capsys):
    exit_code = main([str(FIXTURES / "good"), str(FIXTURES / "good-claims.json"), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["score"] == 20
    assert payload["counts"]["evidenced"] == 1
    assert payload["claims"][0]["id"] == "complete-report"


def test_invalid_claims_return_input_error(capsys, tmp_path):
    invalid = tmp_path / "claims.json"
    invalid.write_text("{}", encoding="utf-8")
    exit_code = main([str(FIXTURES / "good"), str(invalid)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err == "error: claims file must be an object with version 1\n"
