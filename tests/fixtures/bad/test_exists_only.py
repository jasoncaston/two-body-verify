def test_file_exists(output_path):
    assert output_path.exists()
    assert output_path.stat().st_size > 0
