from quart import g, abort, render_template, jsonify
from http import HTTPStatus
import json
from lnbits.decorators import check_user_exists, validate_uuids
from lnbits.extensions.diagonalley import diagonalley_ext

from .crud import (
    create_diagonalleys_product,
    get_diagonalleys_product,
    get_diagonalleys_products,
    delete_diagonalleys_product,
    create_diagonalleys_indexer,
    update_diagonalleys_indexer,
    get_diagonalleys_indexer,
    get_diagonalleys_indexers,
    delete_diagonalleys_indexer,
    create_diagonalleys_order,
    get_diagonalleys_order,
    get_diagonalleys_orders,
    update_diagonalleys_product,
)

@diagonalley_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
async def index():
    return await render_template("diagonalley/index.html", user=g.user)

@diagonalley_ext.route("/<stall_id>")
async def display(stall_id):
    product = await get_diagonalleys_products(stall_id)
    if not product:
        abort(HTTPStatus.NOT_FOUND, "Stall does not exist.")

    return await render_template("diagonalley/stall.html", stall=json.dumps([product._asdict() for product in await get_diagonalleys_products(stall_id)]))
