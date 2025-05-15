import json

import pytest
from typer.testing import CliRunner

from sightcall_scraping.main import app

runner = CliRunner()


@pytest.fixture
def output_file_path(tmp_path):
    file_path = tmp_path / "test.json"
    yield file_path
    if file_path.exists():
        file_path.unlink(missing_ok=True)


def test_cli_scraper_outputs_expected(output_file_path):
    result = runner.invoke(app, ["--max-urls", "1", "--output-file", str(output_file_path)])
    assert result.exit_code == 0
    assert output_file_path.exists()
    with open(output_file_path, "r") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0
