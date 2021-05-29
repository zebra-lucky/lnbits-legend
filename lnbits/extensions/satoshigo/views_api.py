from quart import g, jsonify, request
from http import HTTPStatus
from lnurl.exceptions import InvalidUrl as LnurlInvalidUrl  # type: ignore

from lnbits.core.crud import get_user
from lnbits.decorators import api_check_wallet_key, api_validate_post_request

from . import satoshigo_ext
from .crud import (
    create_satoshigo_game,
    get_satoshigo_game,
    get_satoshigo_games,
    update_satoshigo_game,
    delete_satoshigo_game,
    create_satoshigo_funding,
    get_satoshigo_funding,
    update_satoshigo_funding,
    get_satoshigo_fundings,
)
from ...core.services import create_invoice, check_invoice_status

@satoshigo_ext.route("/api/v1/games", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_games():
    wallet_ids = [g.wallet.id]
    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return jsonify([game._asdict() for game in await get_satoshigo_games(wallet_ids)]), HTTPStatus.OK

@satoshigo_ext.route("/api/v1/games/<game_id>", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_game_retrieve(game_id):
    game = await get_satoshigo_game(game_id)

    if not game:
        return jsonify({"message": "satoshigo game does not exist."}), HTTPStatus.NOT_FOUND

    if game.wallet != g.wallet.id:
        return jsonify({"message": "Not your satoshigo game."}), HTTPStatus.FORBIDDEN

    return jsonify({**game._asdict()}), HTTPStatus.OK


@satoshigo_ext.route("/api/v1/games", methods=["POST"])
@satoshigo_ext.route("/api/v1/games/<game_id>", methods=["PUT"])
@api_check_wallet_key("admin")
@api_validate_post_request(
    schema={
        "title": {"type": "string", "empty": False, "required": True},
    }
)
async def api_game_create_or_update(game_id=None):
    if game_id:
        game = await get_satoshigo_game(game_id)
        if not game:
            return jsonify({"message": "satoshigo game does not exist."}), HTTPStatus.NOT_FOUND
        if game.wallet != g.wallet.id:
            return jsonify({"message": "Not your satoshigo game."}), HTTPStatus.FORBIDDEN
        game = await update_satoshigo_game(game_id, **g.data)
    else:
        game = await create_satoshigo_game(wallet=g.wallet.id, wallet_key=g.wallet.inkey, **g.data)

    return jsonify({**game._asdict()}), HTTPStatus.OK if game_id else HTTPStatus.CREATED


@satoshigo_ext.route("/api/v1/games/<game_id>", methods=["DELETE"])
@api_check_wallet_key("admin")
async def api_game_delete(game_id):
    game = await get_satoshigo_game(game_id)

    if not game:
        return jsonify({"message": "satoshigo game does not exist."}), HTTPStatus.NOT_FOUND

    if game.wallet != g.wallet.id:
        return jsonify({"message": "Not your satoshigo game."}), HTTPStatus.FORBIDDEN

    await delete_satoshigo_game(game_id)

    return "", HTTPStatus.NO_CONTENT


#####################


@satoshigo_ext.route("/api/v1/funding/", methods=["POST"])
@api_validate_post_request(
    schema={
        "game_id": {"type": "string", "empty": False, "required": True},
        "tplat": {"type": "string", "empty": False, "required": True},
        "tplon": {"type": "string", "empty": False, "required": True},
        "btlat": {"type": "string", "empty": False, "required": True},
        "btlon": {"type": "string", "empty": False, "required": True},
        "sats": {"type": "integer", "empty": False, "required": True},
    }
)
async def api_game_fund():
    game = await get_satoshigo_game(g.data["game_id"])

    if not game:
        return jsonify({"message": "satoshigo game does not exist."}), HTTPStatus.NOT_FOUND

    payment_hash, payment_request = await create_invoice(
        wallet_id=game.wallet,
        amount=g.data["sats"],
        memo="game_id",
        )
    
    funding = await create_satoshigo_funding(
        game_id=game.id, 
        wallet=game.wallet, 
        tplat=g.data["tplat"], 
        tplon=g.data["tplon"], 
        btlat=g.data["btlat"], 
        btlon=g.data["btlon"], 
        amount=g.data["sats"], 
        payment_hash=payment_hash,
        )

    return jsonify({**funding._asdict()}, payment_request), HTTPStatus.OK


@satoshigo_ext.route("/api/v1/funding/<satoshigo_id>/<payment_hash>", methods=["GET"])
async def api_game_check_funding(satoshigo_id, payment_hash):
    game = await get_satoshigo_game(satoshigo_id)
    check = await check_invoice_status(game.wallet, payment_hash)
    if not game:
        return jsonify({"message": "Game does not exist."}), HTTPStatus.NOT_FOUND
    if check.paid:
        funding = await update_satoshigo_funding(payment_hash, confirmed=True)
        await update_satoshigo_game(game.id, amount=game.amount + funding.amount)
        return jsonify({**check._asdict()}), HTTPStatus.OK

    return jsonify({**check._asdict()}), HTTPStatus.OK


###################################### PLAYER STUFF 


@satoshigo_ext.route("/api/v1/players", methods=["POST"])
@satoshigo_ext.route("/api/v1/players/<player_id>", methods=["PUT"])
@api_check_wallet_key("admin")
@api_validate_post_request(
    schema={
        "title": {"type": "string", "empty": False, "required": True},
    }
)
async def api_game_player_post():
    return "", HTTPStatus.OK

#registerPlayer
#updatePlayer
#findMe