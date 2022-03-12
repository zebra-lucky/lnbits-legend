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
    delete_game_from_game,
    get_games,
    get_or_create_game_by_wallet,
    set_method,
    update_game,
)
from .models import gameCounter


@eightball_ext.get("/api/v1/currencies")
async def api_list_currencies_available():
    return list(currencies.keys())


@eightball_ext.get("/api/v1/eightball")
async def api_game_from_wallet(
    r: Request, wallet: WalletTypeInfo = Depends(get_key_type)
):
    game = await get_or_create_game_by_wallet(wallet.wallet.id)
    games = await get_games(game.id)

    try:
        return {
            **game.dict(),
            **{"otp_key": game.otp_key, "games": [game.values(r) for game in games]},
        }
    except LnurlInvalidUrl:
        raise HTTPException(
            status_code=HTTPStatus.UPGRADE_REQUIRED,
            detail="LNURLs need to be delivered over a publically accessible `https` domain or Tor.",
        )


class CreategamesData(BaseModel):
    name: str
    description: str
    image: Optional[str]
    price: int
    unit: str


@eightball_ext.post("/api/v1/eightball/games")
@eightball_ext.put("/api/v1/eightball/games/{game_id}")
async def api_add_or_update_game(
    data: CreategamesData, game_id=None, wallet: WalletTypeInfo = Depends(get_key_type)
):
    game = await get_or_create_game_by_wallet(wallet.wallet.id)
    if game_id == None:
        await add_game(
            game.id, data.name, data.description, data.image, data.price, data.unit
        )
        return HTMLResponse(status_code=HTTPStatus.CREATED)
    else:
        await update_game(
            game.id,
            game_id,
            data.name,
            data.description,
            data.image,
            data.price,
            data.unit,
        )


@eightball_ext.delete("/api/v1/eightball/games/{game_id}")
async def api_delete_game(game_id, wallet: WalletTypeInfo = Depends(get_key_type)):
    game = await get_or_create_game_by_wallet(wallet.wallet.id)
    await delete_game_from_game(game.id, game_id)
    raise HTTPException(status_code=HTTPStatus.NO_CONTENT)


class CreateMethodData(BaseModel):
    method: str
    wordlist: Optional[str]


@eightball_ext.put("/api/v1/eightball/method")
async def api_set_method(
    data: CreateMethodData, wallet: WalletTypeInfo = Depends(get_key_type)
):
    method = data.method

    wordlist = data.wordlist.split("\n") if data.wordlist else None
    wordlist = [word.strip() for word in wordlist if word.strip()]

    game = await get_or_create_game_by_wallet(wallet.wallet.id)
    if not game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    updated_game = await set_method(game.id, method, "\n".join(wordlist))
    if not updated_game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    gameCounter.reset(updated_game)
