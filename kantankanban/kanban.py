from typing import Any, Dict, List, NamedTuple
from kantankanban import DB_READ_ERROR
from pathlib import Path
from kantankanban.database import DatabaseHandler
from datetime import datetime


class CurrentCard(NamedTuple):
    card: Dict[str, Any] # I will change this to a real type soon enough.
    error: int

class Kanban:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    # TO DO: erase mentions of priority, add tags. Add ID and title instead
    def add(self, title: List[str], tags: str = '') -> CurrentCard:
        """Add a new card to the database."""
        title_text = " ".join(title)
        card = {
            "Title": title_text,
            "Creation Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        if tags != '':
            card['Tags'] = tags

        # New format I'm imagining: title, category, tags, description, date added
        read = self._db_handler.read_cards() # Let's make this append only soon.
        if read.error == DB_READ_ERROR:
            return CurrentCard(card, read.error)
        read.card_list.append(card)
        write = self._db_handler.write_cards(read.card_list)
        return CurrentCard(card, write.error)

    def remove(self, card_id: int) -> CurrentCard:
        """Remove a card from the board using its id or index."""
        read = self._db_handler.read_cards()
        if read.error:
            return CurrentCard({}, read.error)
        try:
            card = read.card_list.pop(card_id)
        except IndexError:
            return CurrentCard({}, ID_ERROR)
        write = self._db_handler.write_cards(read.card_list)
        return CurrentCard(card, write.error)

    def remove_all(self) -> CurrentCard:
        """Remove all cards from the board."""
        write = self._db_handler.write_cards([])
        return CurrentCard({}, write.error)

    def get_card_list(self) -> List[Dict[str, Any]]:
        """Return the current card list."""
        read = self._db_handler.read_cards()
        return read.card_list