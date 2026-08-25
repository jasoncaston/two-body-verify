def test_file_content(output_path):
    content = output_path.read_text(encoding="utf-8")
    assert "release status: verified" in content
