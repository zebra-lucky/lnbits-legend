import hashlib

from fastapi.params import Query
from lnurl import (  # type: ignore
    LnurlErrorResponse,
    LnurlPayActionResponse,
    LnurlPayResponse,
)
from starlette.requests import Request

from lnbits.core.services import create_invoice
from lnbits.extensions.eightball.models import game
from lnbits.utils.exchange_rates import fiat_amount_as_satoshis

from . import eightball_ext
from .crud import get_game, get_game


@eightball_ext.get("/lnurl/{game_id}", name="eightball.lnurl_response")
async def lnurl_response(req: Request, game_id: int = Query(...)):
    game = await get_game(game_id)  # type: game
    if not game:
        return {"status": "ERROR", "reason": "game not found."}

    if not game.enabled:
        return {"status": "ERROR", "reason": "game disabled."}

    price_msat = (
        await fiat_amount_as_satoshis(game.price, game.unit)
        if game.unit != "sat"
        else game.price
    ) * 1000

    resp = LnurlPayResponse(
        callback=req.url_for("eightball.lnurl_callback", game_id=game.id),
        min_sendable=price_msat,
        max_sendable=price_msat,
        metadata=await game.lnurlpay_metadata(),
    )

    return resp.dict()


@eightball_ext.get("/lnurl/cb/{game_id}", name="eightball.lnurl_callback")
async def lnurl_callback(request: Request, game_id: int):
    game = await get_game(game_id)  # type: game
    if not game:
        return {"status": "ERROR", "reason": "Couldn't find game."}

    if game.unit == "sat":
        min = game.price * 1000
        max = game.price * 1000
    else:
        price = await fiat_amount_as_satoshis(game.price, game.unit)
        # allow some fluctuation (the fiat price may have changed between the calls)
        min = price * 995
        max = price * 1010

    amount_received = int(request.query_params.get("amount") or 0)
    if amount_received < min:
        return LnurlErrorResponse(
            reason=f"Amount {amount_received} is smaller than minimum {min}."
        ).dict()
    elif amount_received > max:
        return LnurlErrorResponse(
            reason=f"Amount {amount_received} is greater than maximum {max}."
        ).dict()

    game = await get_game(game.game)

    try:
        payment_hash, payment_request = await create_invoice(
            wallet_id=game.wallet,
            amount=int(amount_received / 1000),
            memo=game.name,
            description_hash=hashlib.sha256(
                (await game.lnurlpay_metadata()).encode("utf-8")
            ).digest(),
            extra={"tag": "eightball", "game": game.id},
        )
    except Exception as exc:
        return LnurlErrorResponse(reason=exc.message).dict()

    resp = LnurlPayActionResponse(
        pr=payment_request,
        success_action=game.success_action(game, payment_hash, request)
        if game.method
        else None,
        routes=[],
    )

    return resp.dict()
