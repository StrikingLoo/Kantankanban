"""This module provides the RP Card CLI."""
from typing import List, Optional
import typer
from kantankanban import ERRORS, __app_name__, __version__, config, database, kanban
from pathlib import Path
from typing_extensions import Annotated
import os
from enum import Enum

app = typer.Typer()

colors = {
'ERROR' : typer.colors.RED,
'SUCCESS' : typer.colors.GREEN,
'INFO' : typer.colors.CYAN
}
    

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
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The board database is {db_path}", fg=colors['SUCCESS'])
        # Add new board to boards board
        BOARDS_BOARD_NAME = 'boards'
        db_path = database.get_board_path(BOARDS_BOARD_NAME)
        if not os.path.exists(db_path):
            app_init_error = config.init_app(db_path)
            db_init_error = database.init_database(Path(db_path))
        board = get_kanban(BOARDS_BOARD_NAME)
        card, _ = board.add([board_name])

def get_kanban(board_name) -> kanban.Kanban:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH, board_name)
    else:
        typer.secho(
            f'Config file not found. Please, run "kantankanban init {board_name}"',
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)
    if db_path.exists():
        return kanban.Kanban(db_path)
    else:
        typer.secho(
            f'Board {board_name} not found. Please, run "kantankanban init {board_name}"',
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)

@app.command()
def add(
    title: List[str] = typer.Argument(...),
    board_name: str = typer.Option('default', '-n'),
    tags: str = typer.Option('', "--tags", help="Tags as a single string. Separated by commas by convention.")
) -> None:
    """Add a new card with a title."""
    board = get_kanban(board_name)
    card, error = board.add(title, tags)
    
    if error:
        typer.secho(
            f'Adding card failed with "{ERRORS[error]}"', fg=colors['ERROR']
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Card: "{card['Title']}" was added """
            f"""to board {board_name}""",
            fg=colors['SUCCESS'],
        )

@app.command()
def mv(
    src_board_name: str = typer.Option('default', '-s', '--src'),
    dst_board_name: str = typer.Option('default', '-d', '--dst'),
    card_id: int = typer.Argument(...),
) -> None:
    """ Move a card from src to dst board (effectively remove from src and add to dst) """
    src_board = get_kanban(src_board_name)

    card_list = src_board.get_card_list()
    try:
        card = card_list[card_id]
    except IndexError:
        typer.secho("Card index out of bounds.", fg=colors['ERROR'])
        raise typer.Exit(1)
    values = card.values()
    title, creation_date, tags = None, None, ''
    if len(values) == 2:
        title, creation_date = values
    else:
        title, creation_date, tags = values
        tags_exist = True

    _remove(src_board, card_id, src_board_name)

    """Add a new card with a title."""
    dst_board = get_kanban(dst_board_name)
    new_card, error = dst_board.add([title], tags)
    
    if error:
        typer.secho(
            f'Adding card failed with "{ERRORS[error]}"', fg=colors['ERROR']
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Card: "{new_card['Title']}" was added """
            f"""to board {dst_board_name}""",
            fg=colors['SUCCESS'],
        )

@app.command(name="list")
def list_all(board_name: str = typer.Option('default', '-n'),
    show_date: int = typer.Option(0, '-d', '--show-date'),
    show_tags: bool = typer.Option(False, '-t', '--show-tags')
    ) -> None:
    """List all cards."""
    board = get_kanban(board_name)
    card_list = board.get_card_list()
    if len(card_list) == 0:
        typer.secho(
            f"There are no cards in the board \"{board_name}\" yet", fg=colors['INFO']
        )
        raise typer.Exit()

    ### get card data first

    data = {'titles' : [], 'creation_dates': [], 'tags': [] }
    tags_exist = False
    for index, card in enumerate(card_list):
        values = card.values()
        if len(values) == 2:
            title, creation_date = values
            data['tags'].append('')
        else:
            title, creation_date, tags = values
            data['tags'].append(tags)
            tags_exist = True
        data['titles'].append(title)
        data['creation_dates'].append(creation_date)
    if not show_tags:
        tags_exist = False
    if tags_exist:
        max_tag_length = max([len(tag) for tag in data['tags']])
    ### Format and print card data
    typer.secho(f"\nboard - {board_name}:\n", fg=colors['INFO'], bold=True)
    columns = (
        "ID  ",
        "|    Creation Date    " if show_date == 1 else '',
        "| Tags "+' '*(max_tag_length-4) if tags_exist == 1 else '',
        "| Title  ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=colors['INFO'], bold=True)
    typer.secho("-" * len(headers), fg=colors['INFO'])
    for index, title in enumerate(data['titles']):
        creation_date, tags = data['creation_dates'][index], data['tags'][index]

        date_string = f"| {creation_date}{(len(columns[1]) - len(str(creation_date)) - 2) * ' '}"
        tags_string = f"| {tags}{(len(columns[2]) - len(str(tags)) - 2) * ' '}"
        typer.secho(
            f"{index}{(len(columns[0]) - len(str(index))) * ' '}"
            f"{date_string if show_date == 1 else ''}"
            f"{tags_string if tags_exist else ''}"
            f"| {title}",
            fg=colors['INFO'],
        )
    typer.secho("-" * len(headers) + "\n", fg=colors['INFO'])

def _remove(board, card_id, board_name):
    card, error = board.remove(card_id)
    if error:
        typer.secho(
            f'Removing card #{card_id} failed with "{ERRORS[error]}"',
            fg=colors['ERROR'],
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Card #{card_id}: \"{card["Title"]}\" was removed from board {board_name}""",
            fg=colors['SUCCESS'],
        )

@app.command()
def remove(
    board_name: str = typer.Option('default', '-n'),
    card_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a card using its ID."""
    board = get_kanban(board_name)

    if force:
        _remove(board, card_id, board_name)
    else:
        card_list = board.get_card_list()
        try:
            card = card_list[card_id]
        except IndexError:
            typer.secho("Card index out of bounds.", fg=colors['ERROR'])
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete card #{card_id}: \"{card['Title']}\" from board {board_name}?"
        )
        if delete:
            _remove(board, card_id, board_name)
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
                fg=colors['ERROR'],
            )
            raise typer.Exit(1)
        else:
            typer.secho(f"All cards were removed from board \"{board_name}\"", fg=colors['SUCCESS'])
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