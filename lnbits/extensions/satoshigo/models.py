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


class satoshigoPlayer(NamedTuple):
    id: str
    user_name: str
    walletid: str
    adminkey: str
    inkey: str
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoPlayer":
        return cls(**dict(row))


class satoshigoPlayers(NamedTuple):
    inkey: str
    game_id: str
    user_name: str
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoPlayers":
        return cls(**dict(row))