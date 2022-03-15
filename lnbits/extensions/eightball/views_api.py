from http import HTTPStatus
from typing import Optional

from fastapi.params import Depends
from lnurl.exceptions import InvalidUrl as LnurlInvalidUrl
from pydantic.main import BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse  # type: ignore

from lnbits.decorators import WalletTypeInfo, get_key_type
from lnbits.utils.exchange_rates import currencies

from . import eightball_ext
from .crud import (
    add_game,
    delete_game,
    get_games,
)
from lnbits.core.crud import (
    get_wallet,
)


@eightball_ext.get("/api/v1/currencies")
async def api_list_currencies_available():
    return list(currencies.keys())


@eightball_ext.get("/api/v1/eightball")
async def api_game_from_wallet(
    r: Request, wallet: WalletTypeInfo = Depends(get_key_type)
):
    games = await get_games(wallet.wallet.user)

    try:
        return [game.dict() for game in games]
    except LnurlInvalidUrl:
        raise HTTPException(
            status_code=HTTPStatus.UPGRADE_REQUIRED,
            detail="LNURLs need to be delivered over a publically accessible `https` domain or Tor.",
        )


class CreategamesData(BaseModel):
    name: str
    description: str
    wallet: str
    price: int
    wordlist: str


@eightball_ext.post("/api/v1/eightball/games")
async def api_add_or_update_game(
    data: CreategamesData, wallet: WalletTypeInfo = Depends(get_key_type)
):
    theWallet = await get_wallet(data.wallet)
    if not theWallet:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Wrong keys",
        )
    if theWallet.user != wallet.wallet.user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Wrong keys",
        )

    game = await add_game(
        data.name,
        data.description,
        theWallet.user,
        data.wallet,
        data.price,
        data.wordlist,
    )
    if not game:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Failed to get game",
        )
    return game


@eightball_ext.delete("/api/v1/eightball/games/{game_id}")
async def api_delete_game(game_id, wallet: WalletTypeInfo = Depends(get_key_type)):

    return await delete_game(game_id)
    raise HTTPException(status_code=HTTPStatus.NO_CONTENT)
