def test_status(result):
    assert result.returncode == 0
    assert result.status == "verified"
