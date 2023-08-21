# Kantankanban 📌

A Kanban CLI tool. Create boards, add cards to them or remove them. 

Built in Python using Typer, it stores cards as JSON data, trivially exportable and usable in other platforms if desired.

## How to Use 🚀

🌱 Create a new board:

`python -m kantankanban init -n $BOARD_NAME`

🔎 See all available boards:

`python -m kantankanban list -n boards`

📓 List all cards in a board:

`python -m kantankanban list -n $BOARD_NAME` (Yes, the board list is just another meta-board!)

This command will result in something like this:

```
board - Meals:

ID  | Title  
-------------
0   | Curry Masala
1   | Roasted Lamb
2   | Butter Chicken 
3   | Garlic Bread
-------------
```

Add `-d 1` to see cards' creation dates. 🗓

🌷 Add a new card to a board:

`python -m kantankanban add 'Card Title' -n $BOARD_NAME`

💀 Remove a card from a board:

`python -m kantankanban remove $ID -n $BOARD_NAME` (Get the ID by listing the cards. IDs are mutable)

The board name can be omitted in add, list and remove commands, effectively allowing for the tool to be used as a single-board kanban (with board: default) and making the commands less verbose.

🥾 Move a card from one board to another

`python -m kantankanban remove $ID --src $SRC_BOARD_NAME --dst $DST_BOARD_NAME` (Get the ID by listing the cards. IDs are mutable). Moves the card under $ID from source board to destination board. 

This can effectively be used to e.g. track tasks with 3 boards: backlog, to-do, done. The order of the last two arguments is indiferent (Assembly convention possible but discouraged).

### Advanced Feature: Tags

Just like Trello and other similar software, this program supports tags (/labels) in cards.

Add a card with tags:

`python -m kantankanban add 'Card Title' -n $BOARD_NAME -t 'tag1, tag2,...'`

Tags will not be visible by default (and a board without tags won't be affected). If present, you can see them by adding the `--show-tags` / `-t` flag to the `list` command.

For example:

`python -m kantankanban list -n $BOARD_NAME`

Results in:

```
ID  | Title  
-------------
0   | book 1
1   | book 2
2   | book 3
-------------
```

After adding `-t`:

`python -m kantankanban list -n $BOARD_NAME -t`

```
ID  | Tags            | Title  
-----------------------------
0   | English History | book 1
1   | Physics         | book 2
2   | Divination      | book 3
-----------------------------
```

This project is open to user suggestions and contributions. Any feedback will be appreciated!

### Relevant commands

Activate environment: 

`source venv/bin/activate`

Run tests:
`python -m pytest tests`

Initial code and project structure inspired by [RealPython.com](https://realpython.com/python-typer-cli/).

See other projects by me on my [blog](https://strikingloo.github.io/blog/).
