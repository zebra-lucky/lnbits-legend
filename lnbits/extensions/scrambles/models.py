from quart import url_for
from sqlite3 import Row
from typing import NamedTuple
import shortuuid  # type: ignore


class scramblesGame(NamedTuple):
    id: str
    wallet: str
    title: str
    top_left: str
    bottom_right: str
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "scramblesGame":
        return cls(**dict(row))

class scramblesFunding(NamedTuple):
    id: str
    scrambles_id: str
    wallet: str
    top_left: str
    bottom_right: str
    amount: int
    payment_hash: str
    confirmed: bool
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "scramblesFunding":
        return cls(**dict(row))