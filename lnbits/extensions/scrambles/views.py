from quart import g, abort, render_template
from http import HTTPStatus
import pyqrcode
from io import BytesIO
from lnbits.decorators import check_user_exists, validate_uuids

from . import scrambles_ext
from .crud import get_scrambles_game


@scrambles_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
async def index():
    return await render_template("scrambles/index.html", user=g.user)


@scrambles_ext.route("/<game_id>")
async def display(game_id):
    game = await get_scrambles_game(game_id) or abort(HTTPStatus.NOT_FOUND, "scrambles game does not exist.")
    return await render_template("scrambles/display.html", topLeft=game.top_left, bottomRight=game.bottom_right)