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

@satoshigo_ext.route("/test/")
async def test():
    return await render_template("satoshigo/testleaflet.html")


@satoshigo_ext.route("/<game_id>")
async def display(game_id):
    game = await get_satoshigo_game(game_id) or abort(HTTPStatus.NOT_FOUND, "satoshigo game does not exist.")
    return await render_template("satoshigo/display.html", gameAmount=game.amount, game_id=game_id)



##################WEBSOCKET ROUTES########################

# socket_relay is a list where the control panel or
# lnurl endpoints can leave a message for the compose window

socket_relay = {}


@copilot_ext.websocket("/ws/panel/<copilot_id>")
async def ws_panel(copilot_id):
    global socket_relay
    while True:
        data = await websocket.receive()
        socket_relay[copilot_id] = shortuuid.uuid()[:5] + "-" + data + "-" + "none"


@copilot_ext.websocket("/ws/compose/<copilot_id>")
async def ws_compose(copilot_id):
    global socket_relay
    while True:
        data = await websocket.receive()
        await websocket.send(socket_relay[copilot_id])


async def updater(data, comment, copilot):
    global socket_relay
    socket_relay[copilot] = shortuuid.uuid()[:5] + "-" + str(data) + "-" + str(comment)