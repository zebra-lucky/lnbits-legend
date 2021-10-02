from quart import g, jsonify, request
from http import HTTPStatus

from lnbits.core.crud import get_user
from lnbits.decorators import api_check_wallet_key, api_validate_post_request

from . import diagonalley_ext
from .crud import (
    create_diagonalley_product,
    get_diagonalley_product,
    get_diagonalley_products,
    delete_diagonalley_product,
    create_diagonalley_zone,
    update_diagonalley_zone,
    get_diagonalley_zone,
    get_diagonalley_zones,
    delete_diagonalley_zone,
    create_diagonalley_stall,
    update_diagonalley_stall,
    get_diagonalley_stall,
    get_diagonalley_stalls,
    delete_diagonalley_stall,
    create_diagonalley_order,
    get_diagonalley_order,
    get_diagonalley_orders,
    update_diagonalley_product,
    delete_diagonalley_order,
)
from lnbits.core.services import create_invoice
from base64 import urlsafe_b64encode
from uuid import uuid4

# from lnbits.db import open_ext_db

from . import db
from .models import Products, Orders, Stalls

### Products


@diagonalley_ext.route("/api/v1/products", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_products():
    wallet_ids = [g.wallet.id]

    if "all_stalls" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return (
        jsonify(
            [
                product._asdict()
                for product in await get_diagonalley_products(wallet_ids)
            ]
        ),
        HTTPStatus.OK,
    )


@diagonalley_ext.route("/api/v1/products", methods=["POST"])
@diagonalley_ext.route("/api/v1/products/<product_id>", methods=["PUT"])
@api_check_wallet_key(key_type="invoice")
@api_validate_post_request(
    schema={
        "stall": {"type": "string", "empty": False, "required": True},
        "product": {"type": "string", "empty": False, "required": True},
        "description": {"type": "string", "empty": False, "required": True},
        "categories": {"type": "string", "empty": False, "required": True},
        "image": {"type": "string", "empty": False, "required": True},
        "price": {"type": "integer", "min": 0, "required": True},
        "quantity": {"type": "integer", "min": 0, "required": True},
    }
)
async def api_diagonalley_product_create(product_id=None):

    if product_id:
        product = await get_diagonalley_product(product_id)

        if not product:
            return (
                jsonify({"message": "Withdraw product does not exist."}),
                HTTPStatus.NOT_FOUND,
            )

        if product.wallet != g.wallet.id:
            return (
                jsonify({"message": "Not your withdraw product."}),
                HTTPStatus.FORBIDDEN,
            )

        product = await update_diagonalley_product(product_id, **g.data)
    else:
        product = await create_diagonalley_product(wallet_id=g.wallet.id, **g.data)

    return (
        jsonify({**product._asdict()}),
        HTTPStatus.OK if product_id else HTTPStatus.CREATED,
    )


@diagonalley_ext.route("/api/v1/products/<product_id>", methods=["DELETE"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_products_delete(product_id):
    product = await get_diagonalley_product(product_id)

    if not product:
        return jsonify({"message": "Product does not exist."}), HTTPStatus.NOT_FOUND

    if product.wallet != g.wallet.id:
        return jsonify({"message": "Not your Diagon Alley."}), HTTPStatus.FORBIDDEN

    await delete_diagonalley_product(product_id)

    return "", HTTPStatus.NO_CONTENT


# # # Shippingzones


@diagonalley_ext.route("/api/v1/zones", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_zones():
    wallet_ids = [g.wallet.id]

    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return (
        jsonify([zone._asdict() for zone in await get_diagonalley_zones(wallet_ids)]),
        HTTPStatus.OK,
    )


@diagonalley_ext.route("/api/v1/zones", methods=["POST"])
@diagonalley_ext.route("/api/v1/zones/<zone_id>", methods=["PUT"])
@api_check_wallet_key(key_type="invoice")
@api_validate_post_request(
    schema={
        "cost": {"type": "integer", "empty": False, "required": True},
        "countries": {"type": "string", "empty": False, "required": True},
    }
)
async def api_diagonalley_zone_create(zone_id=None):

    if zone_id:
        zone = await get_diagonalley_zone(zone_id)

        if not zone:
            return (
                jsonify({"message": "Zone does not exist."}),
                HTTPStatus.NOT_FOUND,
            )

        if zone.wallet != g.wallet.id:
            return (
                jsonify({"message": "Not your record."}),
                HTTPStatus.FORBIDDEN,
            )

        zone = await update_diagonalley_zone(zone_id, **g.data)
    else:
        zone = await create_diagonalley_zone(wallet=g.wallet.id, **g.data)

    return (
        jsonify({**zone._asdict()}),
        HTTPStatus.OK if zone_id else HTTPStatus.CREATED,
    )


@diagonalley_ext.route("/api/v1/zones/<zone_id>", methods=["DELETE"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_zone_delete(zone_id):
    zone = await get_diagonalley_zone(zone_id)

    if not zone:
        return jsonify({"message": "zone does not exist."}), HTTPStatus.NOT_FOUND

    if zone.wallet != g.wallet.id:
        return jsonify({"message": "Not your zone."}), HTTPStatus.FORBIDDEN

    await delete_diagonalley_zone(zone_id)

    return "", HTTPStatus.NO_CONTENT


# # # Stalls


@diagonalley_ext.route("/api/v1/stalls", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_stalls():
    wallet_ids = [g.wallet.id]

    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return (
        jsonify(
            [stall._asdict() for stall in await get_diagonalley_stalls(wallet_ids)]
        ),
        HTTPStatus.OK,
    )


@diagonalley_ext.route("/api/v1/stalls", methods=["POST"])
@diagonalley_ext.route("/api/v1/stalls/<stall_id>", methods=["PUT"])
@api_check_wallet_key(key_type="invoice")
@api_validate_post_request(
    schema={
        "name": {"type": "string", "empty": False, "required": True},
        "wallet": {"type": "string", "empty": False, "required": True},
        "publickey": {"type": "string", "empty": False, "required": True},
        "privatekey": {"type": "string", "empty": False, "required": True},
        "relays": {"type": "string", "empty": False, "required": True},
        "shippingzones": {"type": "string", "empty": False, "required": True},
    }
)
async def api_diagonalley_stall_create(stall_id=None):

    if stall_id:
        stall = await get_diagonalley_stall(stall_id)

        if not stall:
            return (
                jsonify({"message": "Withdraw stall does not exist."}),
                HTTPStatus.NOT_FOUND,
            )

        if stall.wallet != g.wallet.id:
            return (
                jsonify({"message": "Not your withdraw stall."}),
                HTTPStatus.FORBIDDEN,
            )

        stall = await update_diagonalley_stall(stall_id, **g.data)
    else:
        stall = await create_diagonalley_stall(wallet_id=g.wallet.id, **g.data)

    return (
        jsonify({**stall._asdict()}),
        HTTPStatus.OK if stall_id else HTTPStatus.CREATED,
    )


@diagonalley_ext.route("/api/v1/stalls/<stall_id>", methods=["DELETE"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_stall_delete(stall_id):
    stall = await get_diagonalley_stall(stall_id)

    if not stall:
        return jsonify({"message": "Stall does not exist."}), HTTPStatus.NOT_FOUND

    if stall.wallet != g.wallet.id:
        return jsonify({"message": "Not your Stall."}), HTTPStatus.FORBIDDEN

    await delete_diagonalley_stall(stall_id)

    return "", HTTPStatus.NO_CONTENT


###Orders


@diagonalley_ext.route("/api/v1/orders", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_orders():
    wallet_ids = [g.wallet.id]

    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    try:
        return (
            jsonify(
                [order._asdict() for order in await get_diagonalley_orders(wallet_ids)]
            ),
            HTTPStatus.OK,
        )
    except:
        return (
            jsonify({"message": "We could not retrieve the orders."}),
            HTTPStatus.UPGRADE_REQUIRED,
        )


@diagonalley_ext.route("/api/v1/orders", methods=["POST"])
@api_check_wallet_key(key_type="invoice")
@api_validate_post_request(
    schema={
        "id": {"type": "string", "empty": False, "required": True},
        "address": {"type": "string", "empty": False, "required": True},
        "email": {"type": "string", "empty": False, "required": True},
        "quantity": {"type": "integer", "empty": False, "required": True},
        "shippingzone": {"type": "integer", "empty": False, "required": True},
    }
)
async def api_diagonalley_order_create():
    order = await create_diagonalley_order(wallet_id=g.wallet.id, **g.data)
    return jsonify({**order._asdict()}), HTTPStatus.CREATED


@diagonalley_ext.route("/api/v1/orders/<order_id>", methods=["DELETE"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_order_delete(order_id):
    order = await get_diagonalley_order(order_id)

    if not order:
        return jsonify({"message": "Order does not exist."}), HTTPStatus.NOT_FOUND

    if order.wallet != g.wallet.id:
        return jsonify({"message": "Not your Order."}), HTTPStatus.FORBIDDEN

    await delete_diagonalley_order(order_id)

    return "", HTTPStatus.NO_CONTENT


@diagonalley_ext.route("/api/v1/orders/paid/<order_id>", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_order_paid(order_id):
    await db.execute(
        "UPDATE diagonalley.orders SET paid = ? WHERE id = ?",
        (
            True,
            order_id,
        ),
    )
    return "", HTTPStatus.OK


@diagonalley_ext.route("/api/v1/orders/shipped/<order_id>", methods=["GET"])
@api_check_wallet_key(key_type="invoice")
async def api_diagonalley_order_shipped(order_id):
    await db.execute(
        "UPDATE diagonalley.orders SET shipped = ? WHERE id = ?",
        (
            True,
            order_id,
        ),
    )
    order = await db.fetchone(
        "SELECT * FROM diagonalley.orders WHERE id = ?", (order_id,)
    )

    return (
        jsonify([order._asdict() for order in get_diagonalley_orders(order["wallet"])]),
        HTTPStatus.OK,
    )


###List products based on stall id


@diagonalley_ext.route("/api/v1/stall/products/<stall_id>", methods=["GET"])
async def api_diagonalley_stall_products(stall_id):

    rows = await db.fetchone(
        "SELECT * FROM diagonalley.stalls WHERE id = ?", (stall_id,)
    )
    print(rows[1])
    if not rows:
        return jsonify({"message": "Stall does not exist."}), HTTPStatus.NOT_FOUND

    products = db.fetchone(
        "SELECT * FROM diagonalley.products WHERE wallet = ?", (rows[1],)
    )
    if not products:
        return jsonify({"message": "No products"}), HTTPStatus.NOT_FOUND

    return (
        jsonify(
            [products._asdict() for products in await get_diagonalley_products(rows[1])]
        ),
        HTTPStatus.OK,
    )


###Check a product has been shipped


@diagonalley_ext.route("/api/v1/stall/checkshipped/<checking_id>", methods=["GET"])
async def api_diagonalley_stall_checkshipped(checking_id):
    rows = await db.fetchone(
        "SELECT * FROM diagonalley.orders WHERE invoiceid = ?", (checking_id,)
    )
    return jsonify({"shipped": rows["shipped"]}), HTTPStatus.OK


###Place order


@diagonalley_ext.route("/api/v1/stall/order/<stall_id>", methods=["POST"])
@api_validate_post_request(
    schema={
        "id": {"type": "string", "empty": False, "required": True},
        "email": {"type": "string", "empty": False, "required": True},
        "address": {"type": "string", "empty": False, "required": True},
        "quantity": {"type": "integer", "empty": False, "required": True},
        "shippingzone": {"type": "integer", "empty": False, "required": True},
    }
)
async def api_diagonalley_stall_order(stall_id):
    product = await get_diagonalley_product(g.data["id"])
    shipping = await get_diagonalley_stall(stall_id)

    if g.data["shippingzone"] == 1:
        shippingcost = shipping.zone1cost
    else:
        shippingcost = shipping.zone2cost

    checking_id, payment_request = await create_invoice(
        wallet_id=product.wallet,
        amount=shippingcost + (g.data["quantity"] * product.price),
        memo=g.data["id"],
    )
    selling_id = urlsafe_b64encode(uuid4().bytes_le).decode("utf-8")
    await db.execute(
        """
            INSERT INTO diagonalley.orders (id, productid, wallet, product, quantity, shippingzone, address, email, invoiceid, paid, shipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            selling_id,
            g.data["id"],
            product.wallet,
            product.product,
            g.data["quantity"],
            g.data["shippingzone"],
            g.data["address"],
            g.data["email"],
            checking_id,
            False,
            False,
        ),
    )
    return (
        jsonify({"checking_id": checking_id, "payment_request": payment_request}),
        HTTPStatus.OK,
    )
