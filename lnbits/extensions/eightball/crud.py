from typing import List, Optional

from lnbits.db import SQLITE
from . import db
from .wordlists import animals
from .models import game, game


async def add_game(
    name: str, description: str, image: Optional[str], price: int, unit: str
) -> int:
    result = await db.execute(
        """
        INSERT INTO eightball.games (game, name, description, image, price, unit)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (game, name, description, image, price, unit),
    )
    return result._result_proxy.lastrowid


async def update_game(
    game_id: int,
    name: str,
    description: str,
    image: Optional[str],
    price: int,
    unit: str,
) -> int:
    await db.execute(
        """
        UPDATE eightball.games SET
          name = ?,
          description = ?,
          wallet = ?,
          image = ?,
          price = ?,
          unit = ?,
          wordlist = ?
        WHERE game = ? AND id = ?
        """,
        (name, description, image, price, unit, game, game_id),
    )
    return game_id


async def get_game(id: int) -> Optional[game]:
    row = await db.fetchone(
        "SELECT * FROM eightball.games WHERE id = ?  LIMIT 1", (id,)
    )
    return game(**dict(row)) if row else None


async def get_games(game: int) -> List[game]:
    rows = await db.fetchall("SELECT * FROM eightball.games WHERE game = ?", (game,))
    return [game(**dict(row)) for row in rows]


async def delete_game_from_game(game: int, game_id: int):
    await db.execute(
        """
        DELETE FROM eightball.games WHERE game = ? AND id = ?
        """,
        (game, game_id),
    )
