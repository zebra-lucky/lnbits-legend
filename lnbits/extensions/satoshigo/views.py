from quart import g, abort, render_template
from http import HTTPStatus
import pyqrcode
from io import BytesIO
from lnbits.decorators import check_user_exists, validate_uuids

from . import satoshigo_ext
from .crud import get_satoshigo_game


@satoshigo_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
async def index():
    return await render_template("satoshigo/index.html", user=g.user)


@satoshigo_ext.route("/<game_id>")
async def display(game_id):
    game = await get_satoshigo_game(game_id) or abort(HTTPStatus.NOT_FOUND, "satoshigo game does not exist.")
    print(game)
    return await render_template("satoshigo/display.html", topLeft=game.top_left, bottomRight=game.bottom_right, gameAmount=game.amount, )