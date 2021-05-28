from quart import url_for
from sqlite3 import Row
from typing import NamedTuple
import shortuuid  # type: ignore


class satoshigoGame(NamedTuple):
    id: str
    wallet: str
    wallet_key: str
    title: str
    coins: str
    render_pin: int
    amount: int
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoGame":
        return cls(**dict(row))

class satoshigoFunding(NamedTuple):
    id: str
    satoshigo_id: str
    wallet: str
    tplat: str
    tplon: str
    btlat: str
    btlon: str
    amount: int
    payment_hash: str
    confirmed: bool
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoFunding":
        return cls(**dict(row))