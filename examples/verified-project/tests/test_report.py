from pathlib import Path

from report import write_report


def test_report_value(tmp_path):
    output = tmp_path / "report.txt"
    write_report(output)
    assert "status: verified" in output.read_text(encoding="utf-8")
