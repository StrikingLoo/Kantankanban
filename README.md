# Kantankanban

A Kantan CLI tool. Create boards, add cards to them or remove them.

## Example Usage

First, initialize a new board:

`python -m kantakanban init -n $BOARD_NAME`

See all available boards:

`python -m kantakanban list -n boards`

See all cards in a board:

`python -m kantakanban list -n $BOARD_NAME` (Yes, the board list is just another meta-board!)

Add `-d 1` to see card creation date.

Add a new card to a board:

`python -m kantakanban add 'Card Title' -n $BOARD_NAME`

Remove a card from a board:

`python -m kantakanban remove $ID -n $BOARD_NAME` (Get the ID by listing the cards. IDs are mutable)

## Future Updates

Will soon add

- Tag functionality (including tag-based search)
- `mv` command to transfer a card from one board to another
- Anything else I can think of, or any user suggests

### Relevant commands

Activate environment: 

`source venv/bin/activate`

Run tests:
`python -m pytest tests`

Initial code and project structure inspired by [RealPython.com](https://realpython.com/python-typer-cli/).

See other projects by me on my [blog](https://strikingloo.github.io).
