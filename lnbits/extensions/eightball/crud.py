from typing import List, Optional

from lnbits.db import SQLITE
from . import db
from .wordlists import phrases
from .models import game, game
from lnbits.helpers import urlsafe_short_hash


async def add_game(
    name: str,
    description: str,
    wallet: str,
    price: int,
    unit: str,
    wordlist: str,
) -> int:
    game_id = urlsafe_short_hash()
    result = await db.execute(
        """
        INSERT INTO eightball.games (game_id, name, description, wallet, price, unit, wordlist)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (game_id, name, description, wallet, price, unit, wordlist),
    )
    return result._result_proxy.lastrowid


async def update_game(
    game_id: str,
    name: str,
    description: str,
    wallet: str,
    price: int,
    unit: str,
    wordlist: str,
) -> int:
    await db.execute(
        """
        UPDATE eightball.games SET
          name = ?,
          description = ?,
          wallet = ?,
          price = ?,
          unit = ?,
          wordlist = ?
        WHERE id = ?
        """,
        (name, description, wallet, price, unit, wordlist, game_id),
    )
    return game_id


async def get_game(id: str) -> Optional[game]:
    row = await db.fetchone("SELECT * FROM eightball.games WHERE id", (id,))
    return game(**dict(row)) if row else None


async def get_games(wallet: str) -> List[game]:
    rows = await db.fetchall(
        "SELECT * FROM eightball.games WHERE wallet = ?", (wallet,)
    )
    return [game(**dict(row)) for row in rows]


async def delete_game_from_game(game_id: int):
    await db.execute(
        """
        DELETE FROM eightball.games WHERE id = ?
        """,
        (game_id),
    )
