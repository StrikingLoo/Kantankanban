from typer.testing import CliRunner
from kantankanban import (DB_READ_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    kanban)
import json

import pytest
from typer.testing import CliRunner

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_json_file(tmp_path):
    todo = [{"Description": "Get some milk"}]
    db_file = tmp_path / "todo.json"
    with db_file.open("w") as db:
        json.dump(todo, db, indent=4)
    return db_file

test_data1 = {
    "description": ["Clean", "the", "house"],
    "todo": {
        "Title": "Clean the house",
    },
}
test_data2 = {
    "description": ["Wash the car"],
    "todo": {
        "Title": "Wash the car",
    },
}

@pytest.mark.parametrize(
    "description, expected",
    [
        pytest.param(
            test_data1["description"],
            (test_data1["todo"], SUCCESS),
        ),
        pytest.param(
            test_data2["description"],
            (test_data2["todo"], SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, description, expected):
    todoer = kanban.Kanban(mock_json_file)
    result = todoer.add(description, '')
    assert result.card['Title'] == expected[0]['Title']
    read = todoer._db_handler.read_cards()
    assert len(read.card_list) == 2