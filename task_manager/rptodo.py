from typing import Any, Dict, List, NamedTuple
from task_manager import DB_READ_ERROR
from pathlib import Path
from task_manager.database import DatabaseHandler

class CurrentTodo(NamedTuple):
    todo: Dict[str, Any] # I will change this to a real type soon enough.
    error: int

class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    # TO DO: erase mentions of priority, add tags. Add ID and title instead
    def add(self, title: List[str]) -> CurrentTodo:
        """Add a new to-do to the database."""
        title_text = " ".join(title)
        todo = {
            "Title": title_text,
        }
        # New format I'm imagining: title, category, tags, description, date added
        read = self._db_handler.read_todos() # Let's make this append only soon.
        if read.error == DB_READ_ERROR:
            return CurrentTodo(todo, read.error)
        read.todo_list.append(todo)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def remove(self, todo_id: int) -> CurrentTodo:
        """Remove a card from the board using its id or index."""
        read = self._db_handler.read_todos()
        if read.error:
            return CurrentTodo({}, read.error)
        try:
            todo = read.todo_list.pop(todo_id)
        except IndexError:
            return CurrentTodo({}, ID_ERROR)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def remove_all(self) -> CurrentTodo:
        """Remove all cards from the board."""
        write = self._db_handler.write_todos([])
        return CurrentTodo({}, write.error)

    def get_todo_list(self) -> List[Dict[str, Any]]:
        """Return the current card list."""
        read = self._db_handler.read_todos()
        return read.todo_list

'''
class Card():

    def __init__(self, title, priority):
        self.title = title
        self.priority = priority

    title: str
    priority: int

    def __str__(self):
        return f'\{title: {self.title}, priority: {self.priority}\}'
'''