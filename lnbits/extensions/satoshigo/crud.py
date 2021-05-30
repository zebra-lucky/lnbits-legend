import random
from datetime import datetime
from typing import List, Optional, Union
from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import satoshigoGame, satoshigoFunding, satoshigoPlayers
from ..usermanager.crud import create_usermanager_user, get_usermanager_user, get_usermanager_users_wallets

async def create_satoshigo_game(
    *,
    wallet: str,
    wallet_key: str,
    title: str,
) -> satoshigoGame:
    game_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_game (
            id,
            wallet,
            wallet_key,
            title,
            coins,
            amount,
            render_pin
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            wallet,
            wallet_key,
            title,
            "",
            0,
            random.randint(999, 9999)

        ),
    )
    game = await get_satoshigo_game(game_id)
    assert game, "Newly created game couldn't be retrieved"
    return game


async def get_satoshigo_game(game_id: str) -> Optional[satoshigoGame]:
    row = await db.fetchone("SELECT * FROM satoshigo_game WHERE id = ?", (game_id,))
    return satoshigoGame._make(row)


async def get_satoshigo_games(wallet_ids: Union[str, List[str]]) -> List[satoshigoGame]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(f"SELECT * FROM satoshigo_game WHERE wallet IN ({q})", (*wallet_ids,))

    return [satoshigoGame.from_row(row) for row in rows]


async def update_satoshigo_game(game_id: str, **kwargs) -> Optional[satoshigoGame]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(f"UPDATE satoshigo_game SET {q} WHERE id = ?", (*kwargs.values(), game_id))
    row = await db.fetchone("SELECT * FROM satoshigo_game WHERE id = ?", (game_id,))
    return satoshigoGame.from_row(row) if row else None


async def delete_satoshigo_game(game_id: str) -> None:
    await db.execute("DELETE FROM satoshigo_game WHERE id = ?", (game_id,))

###############

async def create_satoshigo_funding(
    *,
    game_id: str,
    wallet: str,
    tplat: str,
    tplon: str,
    btlat: str,
    btlon: str,
    amount: int,
    payment_hash: str
) -> satoshigoGame:
    funding_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_funding (
            id,
            satoshigo_id,
            wallet,
            tplat,
            tplon,
            btlat,
            btlon,
            amount,
            payment_hash,
            confirmed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (   
            funding_id,
            game_id,
            wallet,
            tplat,
            tplon,
            btlat,
            btlon,
            amount,
            payment_hash,
            False
        ),
    )
    funding = await get_satoshigo_funding(funding_id)
    assert funding, "Newly created funding couldn't be retrieved"
    return funding

async def get_satoshigo_funding(funding_id: str) -> Optional[satoshigoFunding]:
    row = await db.fetchone("SELECT * FROM satoshigo_funding WHERE id = ?", (funding_id,))
    return satoshigoFunding._make(row)


async def get_satoshigo_fundings(game_id: str) -> Optional[satoshigoFunding]:
    row = await db.fetchall("SELECT * FROM satoshigo_funding WHERE game_id = ?", (game_id,))
    return satoshigoFunding._make(row)

async def update_satoshigo_funding(payment_hash: str, **kwargs) -> Optional[satoshigoFunding]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE satoshigo_funding SET {q} WHERE payment_hash = ?", (*kwargs.values(), payment_hash)
    )
    row = await db.fetchone("SELECT * FROM satoshigo_funding WHERE payment_hash = ?", (payment_hash,))
    return satoshigoFunding._make(row)


###########################PLAYER

async def create_satoshigo_player(data):
    player = await create_usermanager_user(**data)
    await db.execute(
        """
        INSERT INTO satoshigo_players (
            id,
            admin
        )
        VALUES (?, ?)
        """,
        (   
         player.id,
         player.admin
        ),
    )
    assert player, "Newly created game couldn't be retrieved"
    return player

async def get_satoshigo_player(player_id):
    player = await get_usermanager_user(player_id)
    return player

async def get_satoshigo_player_wallet(player_id):
    wallet = await get_usermanager_users_wallets(player_id)
    return wallet

async def get_satoshigo_players(admin) -> Optional[satoshigoPlayers]:
    rows = await db.fetchall("SELECT * FROM satoshigo_players WHERE admin = ?", (admin,))
    return [satoshigoPlayers._make(row) for row in rows]