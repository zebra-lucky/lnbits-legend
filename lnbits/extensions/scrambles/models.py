from quart import url_for
from sqlite3 import Row
from typing import NamedTuple
import shortuuid  # type: ignore


class scramblesgame(NamedTuple):
    id: str
    wallet: str
    title: str
    top_left: str
    bottom_right: str

    @classmethod
    def from_row(cls, row: Row) -> "scramblesgame":
        return cls(**dict(row))