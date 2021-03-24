from quart import g, jsonify, request
from http import HTTPStatus
from lnurl.exceptions import InvalidUrl as LnurlInvalidUrl  # type: ignore

from lnbits.core.crud import get_user
from lnbits.decorators import api_check_wallet_key, api_validate_post_request

from . import scrambles_ext
from .crud import (
    create_scrambles_game,
    get_scrambles_game,
    get_scrambles_games,
    update_scrambles_game,
    delete_scrambles_game,
    create_scrambles_funding,
    get_scrambles_funding,
    get_scrambles_fundings,
)
from ...core.services import create_invoice

@scrambles_ext.route("/api/v1/games", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_games():
    wallet_ids = [g.wallet.id]
    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return jsonify([game._asdict() for game in await get_scrambles_games(wallet_ids)]), HTTPStatus.OK

@scrambles_ext.route("/api/v1/games/<game_id>", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_game_retrieve(game_id):
    game = await get_scrambles_game(game_id)

    if not game:
        return jsonify({"message": "scrambles game does not exist."}), HTTPStatus.NOT_FOUND

    if game.wallet != g.wallet.id:
        return jsonify({"message": "Not your scrambles game."}), HTTPStatus.FORBIDDEN

    return jsonify({**game._asdict()}), HTTPStatus.OK


@scrambles_ext.route("/api/v1/games", methods=["POST"])
@scrambles_ext.route("/api/v1/games/<game_id>", methods=["PUT"])
@api_check_wallet_key("admin")
@api_validate_post_request(
    schema={
        "title": {"type": "string", "empty": False, "required": True},
        "top_left": {"type": "string", "empty": False, "required": True},
        "bottom_right": {"type": "string", "empty": False, "required": True},
    }
)
async def api_game_create_or_update(game_id=None):
    if game_id:
        game = await get_scrambles_game(game_id)
        if not game:
            return jsonify({"message": "scrambles game does not exist."}), HTTPStatus.NOT_FOUND
        if game.wallet != g.wallet.id:
            return jsonify({"message": "Not your scrambles game."}), HTTPStatus.FORBIDDEN
        game = await update_scrambles_game(game_id, **g.data)
    else:
        game = await create_scrambles_game(wallet=g.wallet.id, **g.data)

    return jsonify({**game._asdict()}), HTTPStatus.OK if game_id else HTTPStatus.CREATED


@scrambles_ext.route("/api/v1/games/<game_id>", methods=["DELETE"])
@api_check_wallet_key("admin")
async def api_game_delete(game_id):
    game = await get_scrambles_game(game_id)

    if not game:
        return jsonify({"message": "scrambles game does not exist."}), HTTPStatus.NOT_FOUND

    if game.wallet != g.wallet.id:
        return jsonify({"message": "Not your scrambles game."}), HTTPStatus.FORBIDDEN

    await delete_scrambles_game(game_id)

    return "", HTTPStatus.NO_CONTENT


#####################


@scrambles_ext.route("/api/v1/funding/", methods=["POST"])
@api_validate_post_request(
    schema={
        "game_id": {"type": "string", "empty": False, "required": True},
        "top_left": {"type": "string", "empty": False, "required": True},
        "bottom_right": {"type": "string", "empty": False, "required": True},
        "sats": {"type": "integer", "empty": False, "required": True},
    }
)
async def api_game_fund():
    game = await get_scrambles_game(g.data["game_id"])

    if not game:
        return jsonify({"message": "scrambles game does not exist."}), HTTPStatus.NOT_FOUND

    payment_hash, payment_request = await create_invoice(
        wallet_id=game.wallet,
        amount=g.data["sats"],
        memo="game_id",
        )
    
    funding = await create_scrambles_funding(
        game_id=game.id, 
        wallet=game.wallet, 
        top_left=g.data["top_left"], 
        bottom_right=g.data["bottom_right"], 
        amount=g.data["sats"], 
        payment_hash=payment_hash,
        )

    return jsonify({**funding._asdict()}), HTTPStatus.OK


@scrambles_ext.route("/api/v1/funding/<funding_id>", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_game_check_funding(funding_id):
    game = await get_scrambles_game(funding_id)

    if not game:
        return jsonify({"message": "scrambles game does not exist."}), HTTPStatus.NOT_FOUND

    if game.wallet != g.wallet.id:
        return jsonify({"message": "Not your scrambles game."}), HTTPStatus.FORBIDDEN

    return jsonify({**game._asdict()}), HTTPStatus.OK