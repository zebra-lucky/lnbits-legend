from datetime import datetime
from typing import List, Optional, Union
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import scramblesGame, scramblesFunding


async def create_scrambles_game(
    *,
    wallet: str,
    title: str,
    top_left: str,
    bottom_right: str,
) -> scramblesGame:
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
            wallet,
            title,
            top_left,
            bottom_right,
        ),
    )
    game = await get_scrambles_game(game_id)
    assert game, "Newly created game couldn't be retrieved"
    return game


async def get_scrambles_game(game_id: str) -> Optional[scramblesGame]:
    row = await db.fetchone("SELECT * FROM scrambles_game WHERE id = ?", (game_id,))
    return scramblesGame._make(row)


async def get_scrambles_games(wallet_ids: Union[str, List[str]]) -> List[scramblesGame]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(f"SELECT * FROM scrambles_game WHERE wallet IN ({q})", (*wallet_ids,))

    return [scramblesGame.from_row(row) for row in rows]


async def update_scrambles_game(game_id: str, **kwargs) -> Optional[scramblesgame]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(f"UPDATE scrambles_game SET {q} WHERE id = ?", (*kwargs.values(), game_id))
    row = await db.fetchone("SELECT * FROM scrambles_game WHERE id = ?", (game_id,))
    return scramblesGame.from_row(row) if row else None


async def delete_scrambles_game(game_id: str) -> None:
    await db.execute("DELETE FROM scrambles_game WHERE id = ?", (game_id,))

###############

async def create_scrambles_funding(
    *,
    game_id: str,
    wallet: str,
    top_left: str,
    bottom_right: str,
    amount: int,
    payment_hash: str
) -> scramblesGame:
    funding_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO scrambles_game (
            id,
            game_id,
            wallet,
            top_left,
            bottom_right,
            amount,
            payment_hash,
            confirmed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (   
            funding_id,
            game_id,
            wallet,
            top_left,
            bottom_right,
            amount,
            payment_hash,
            False
        ),
    )
    funding = await get_scrambles_funding(funding_id)
    assert funding, "Newly created game couldn't be retrieved"
    return funding

async def get_scrambles_funding(funding_id: str) -> Optional[scramblesFunding]:
    row = await db.fetchone("SELECT * FROM scrambles_funding WHERE id = ?", (funding_id,))
    return scramblesFunding._make(row)


async def get_scrambles_fundings(game_id: str) -> Optional[scramblesFunding]:
    row = await db.fetchall("SELECT * FROM scrambles_funding WHERE game_id = ?", (game_id,))
    return scramblesFunding._make(row)