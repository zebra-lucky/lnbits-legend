from datetime import datetime
from typing import List, Optional, Union
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import scramblesgame


async def create_scrambles_game(
    *,
    wallet_id: str,
    title: str,
    top_left: str,
    bottom_right: str,
) -> scramblesgame:
    game_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO scrambles_game (
            id,
            wallet,
            title,
            top_left,
            bottom_right
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            game_id,
            wallet_id,
            title,
            top_left,
            bottom_right,
        ),
    )
    game = await get_scrambles_game(game_id)
    assert game, "Newly created game couldn't be retrieved"
    return game


async def get_scrambles_game(game_id: str) -> Optional[scramblesgame]:
    row = await db.fetchone("SELECT * FROM scrambles_game WHERE id = ?", (game_id,))
    return scramblesgame._make(row)


async def get_scrambles_games(wallet_ids: Union[str, List[str]]) -> List[scramblesgame]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(f"SELECT * FROM scrambles_game WHERE wallet IN ({q})", (*wallet_ids,))

    return [scramblesgame.from_row(row) for row in rows]


async def update_scrambles_game(game_id: str, **kwargs) -> Optional[scramblesgame]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(f"UPDATE scrambles_game SET {q} WHERE id = ?", (*kwargs.values(), game_id))
    row = await db.fetchone("SELECT * FROM scrambles_game WHERE id = ?", (game_id,))
    return scramblesgame.from_row(row) if row else None


async def delete_scrambles_game(game_id: str) -> None:
    await db.execute("DELETE FROM scrambles_game WHERE id = ?", (game_id,))