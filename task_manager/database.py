"""This module provides the database functionality."""

import configparser
from pathlib import Path
import json
from typing import Any, Dict, List, NamedTuple
from task_manager import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_task.json"
)

def get_board_path(board_name) -> Path:
    return Path.home().joinpath(
    "." + board_name + "_board.json")

def get_database_path(config_file: Path, board_name: str) -> Path:
    """Return the current path to the to-do database."""
    if board_name != '':
        return get_board_path(board_name)
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """Create the to-do database."""
    try:
        db_path.write_text("[]")  # Empty to-do list
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR

class DBResponse(NamedTuple):
    todo_list: List[Dict[str, Any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_todos(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse([], JSON_ERROR)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)

    def write_todos(self, todo_list: List[Dict[str, Any]]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(todo_list, db, indent=4)
            return DBResponse(todo_list, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(todo_list, DB_WRITE_ERROR)