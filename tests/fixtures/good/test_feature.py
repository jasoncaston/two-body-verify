from feature import export_report


def test_export_report(tmp_path):
    export_report(tmp_path / "result.txt")
