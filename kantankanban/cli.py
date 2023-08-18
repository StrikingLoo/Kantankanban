"""This module provides the RP To-Do CLI."""
from typing import List, Optional
import typer
from kantankanban import ERRORS, __app_name__, __version__, config, database, kanban
from pathlib import Path
from typing_extensions import Annotated
import os

app = typer.Typer()

@app.command()
def init(
    board_name: str = typer.Option(
        'default',
        "--name",
        "-n",
        prompt="board name?",
    ),
) -> None:
    """Initialize a new board."""
    db_path = database.get_board_path(board_name)
    if os.path.exists(db_path):
        typer.secho(
            f'Board \"{board_name}\" already exists.',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The board database is {db_path}", fg=typer.colors.GREEN)
        # Add new board to boards board
        BOARDS_BOARD_NAME = 'boards'
        db_path = database.get_board_path(BOARDS_BOARD_NAME)
        app_init_error = config.init_app(db_path)
        db_init_error = database.init_database(Path(db_path))
        board = get_kanban(BOARDS_BOARD_NAME)
        todo, _ = board.add([board_name])

def get_kanban(board_name) -> kanban.Kanban:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH, board_name)
    else:
        typer.secho(
            'Config file not found. Please, run "kantankanban init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return kanban.Kanban(db_path)
    else:
        typer.secho(
            f'Board {board_name} not found. Please, run "kantankanban init {board_name}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

@app.command()
def add(
    board_name: str = typer.Option('default', '-n'),
    title: List[str] = typer.Argument(...),
) -> None:
    """Add a new card with a title."""
    board = get_kanban(board_name)
    todo, error = board.add(title)
    if error:
        typer.secho(
            f'Adding card failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Card: "{todo['Title']}" was added """
            f"""to board {board_name}""",
            fg=typer.colors.GREEN,
        )

@app.command(name="list")
def list_all(board_name: str = typer.Option('default', '-n')) -> None:
    """List all cards."""
    board = get_kanban(board_name)
    todo_list = board.get_todo_list()
    if len(todo_list) == 0:
        typer.secho(
            f"There are no cards in the board \"{board_name}\" yet", fg=typer.colors.CYAN
        )
        raise typer.Exit()
    typer.secho(f"\nboard - {board_name}:\n", fg=typer.colors.CYAN, bold=True)
    columns = (
        "ID  ",
        "| Title  ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.CYAN, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.CYAN)
    for index, todo in enumerate(todo_list):
        title = list(todo.values())[0] # ugly and will be fixed
        typer.secho(
            f"{index}{(len(columns[0]) - len(str(index))) * ' '}"
            #f"| ({priority}){(len(columns[1]) - len(str(priority)) - 4) * ' '}"
            #f"| {done}{(len(columns[2]) - len(str(done)) - 2) * ' '}"
            f"| {title}",
            fg=typer.colors.CYAN,
        )
    typer.secho("-" * len(headers) + "\n", fg=typer.colors.CYAN)

@app.command()
def remove(
    board_name: str = typer.Option('default', '-n'),
    todo_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a card using its ID."""
    board = get_kanban(board_name)

    def _remove():
        todo, error = board.remove(todo_id)
        if error:
            typer.secho(
                f'Removing card #{todo_id} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""Card #{todo_id}: '{todo["Title"]}' was removed from board {board_name}""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        todo_list = board.get_todo_list()
        try:
            todo = todo_list[todo_id]
        except IndexError:
            typer.secho("Invalid TODO_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete card #{todo_id}: \"{todo['Title']}\" from board {board_name}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")

@app.command(name="clear")
def remove_all(
    board_name: str = typer.Option('default', '-n'),
    force: bool = typer.Option(
        ...,
        prompt=f"Delete all cards from board?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove all cards from a board."""
    board = get_kanban(board_name)
    if force:
        error = board.remove_all().error
        if error:
            typer.secho(
                f'Removing cards failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(f"All cards were removed from board \"{board_name}\"", fg=typer.colors.GREEN)
    else:
        typer.echo("Operation canceled")

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

# priority: int = typer.Option(2, "--priority", "-p", min=1, max=5),