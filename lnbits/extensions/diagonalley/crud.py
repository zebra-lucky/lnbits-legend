from base64 import urlsafe_b64encode
from uuid import uuid4
from typing import List, Optional, Union

from lnbits.settings import WALLET
# from lnbits.db import open_ext_db
from lnbits.db import SQLITE
from . import db
from .models import Products, Orders, Indexers

import httpx
from lnbits.helpers import urlsafe_short_hash
import re

regex = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


###Products

async def create_diagonalleys_product(
    *,
    wallet_id: str,
    product: str,
    categories: str,
    description: str,
    image: Optional[str] = None,
    price: int,
    quantity: int,
) -> Products:
    returning = "" if db.type == SQLITE else "RETURNING ID"
    method = db.execute if db.type == SQLITE else db.fetchone
    product_id = urlsafe_short_hash()
    # with open_ext_db("diagonalley") as db:
    result = await (method)(
        f"""
        INSERT INTO diagonalley.products (id, wallet, product, categories, description, image, price, quantity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        {returning}
        """,
        (
            product_id,
            wallet_id,
            product,
            categories,
            description,
            image,
            price,
            quantity,
        ),
    )
    product = await get_diagonalleys_product(product_id)
    assert product, "Newly created product couldn't be retrieved"
    return product


async def update_diagonalleys_product(product_id: str, **kwargs) -> Optional[Indexers]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])

    # with open_ext_db("diagonalley") as db:
    await db.execute(
        f"UPDATE diagonalley.products SET {q} WHERE id = ?",
        (*kwargs.values(), product_id),
    )
    row = await db.fetchone(
        "SELECT * FROM diagonalley.products WHERE id = ?", (product_id,)
    )

    return get_diagonalleys_indexer(product_id)


async def get_diagonalleys_product(product_id: str) -> Optional[Products]:
    row = await db.fetchone("SELECT * FROM diagonalley.products WHERE id = ?", (product_id,))
    return Products.from_row(row) if row else None


async def get_diagonalleys_products(wallet_ids: Union[str, List[str]]) -> List[Products]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    # with open_ext_db("diagonalley") as db:
    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"""
        SELECT * FROM diagonalley.products WHERE wallet IN ({q})
        """,
        (*wallet_ids,)
    )
    return [Products.from_row(row) for row in rows]


async def delete_diagonalleys_product(product_id: str) -> None:
    await db.execute("DELETE FROM diagonalley.products WHERE id = ?", (product_id,))


###Indexers


async def create_diagonalleys_indexer(
    *,
    wallet_id: str,
    shopname: str,
    indexeraddress: str,
    shippingzone1: str,
    shippingzone2: str,
    zone1cost: int,
    zone2cost: int,
    email: str,
) -> Indexers:

    returning = "" if db.type == SQLITE else "RETURNING ID"
    method = db.execute if db.type == SQLITE else db.fetchone

    indexer_id = urlsafe_short_hash()
    result = await (method)(
        f"""
        INSERT INTO diagonalley.indexers (
            id,
            wallet,
            shopname,
            indexeraddress,
            online,
            rating,
            shippingzone1,
            shippingzone2,
            zone1cost,
            zone2cost,
            email
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        {returning}
        """,
        (
            indexer_id,
            wallet_id,
            shopname,
            indexeraddress,
            False,
            0,
            shippingzone1,
            shippingzone2,
            zone1cost,
            zone2cost,
            email,
        ),
    )
    #if db.type == SQLITE:
    #    indexer_id = result._result_proxy.lastrowid
    #else:
    #    indexer_id = result[0]

    indexer = await get_diagonalleys_indexer(indexer_id)
    assert indexer, "Newly created indexer couldn't be retrieved"
    return indexer


async def update_diagonalleys_indexer(indexer_id: str, **kwargs) -> Optional[Indexers]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE diagonalley.indexers SET {q} WHERE id = ?", (*kwargs.values(), indexer_id),
    )
    row = await db.fetchone("SELECT * FROM diagonalley.indexers WHERE id = ?", (indexer_id,))
    return Indexers.from_row(row) if row else None


async def get_diagonalleys_indexer(indexer_id: str) -> Optional[Indexers]:
    roww = await db.fetchone(
        "SELECT * FROM diagonalley.indexers WHERE id = ?", (indexer_id,)
    )

    try:
        x = httpx.get(roww["indexeraddress"] + "/" + roww["ratingkey"])
        if x.status_code == 200:
            print(x)
            print("poo")
            await db.execute(
                "UPDATE diagonalley.indexers SET online = ? WHERE id = ?",
                (
                    True,
                    indexer_id,
                ),
            )
        else:
            await db.execute("UPDATE diagonalley.indexers SET online = ? WHERE id = ?", (False, indexer_id,),)
    except:
        print("An exception occurred")

    #with open_ext_db("diagonalley") as db:
    row = await db.fetchone("SELECT * FROM diagonalley.indexers WHERE id = ?", (indexer_id,))
    return Indexers.from_row(row) if row else None


async def get_diagonalleys_indexers(wallet_ids: Union[str, List[str]]) -> List[Indexers]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM diagonalley.indexers WHERE wallet IN ({q})", (*wallet_ids,)
    )

    for r in rows:
        try:
            x = httpx.get(r["indexeraddress"] + "/" + r["ratingkey"])
            if x.status_code == 200:
                await db.execute(
                        "UPDATE diagonalley.indexers SET online = ? WHERE id = ?",
                        (
                            True,
                            r["id"],
                        ),
                    )
            else:
                await db.execute(
                        "UPDATE diagonalley.indexers SET online = ? WHERE id = ?",
                        (
                            False,
                            r["id"],
                        ),
                )
        except:
            print("An exception occurred")
    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM diagonalley.indexers WHERE wallet IN ({q})", (*wallet_ids,)
    )
    return [Indexers.from_row(row) for row in rows]


async def delete_diagonalleys_indexer(indexer_id: str) -> None:
    await db.execute("DELETE FROM diagonalley.indexers WHERE id = ?", (indexer_id,))


###Orders


async def create_diagonalleys_order(
    *,
    productid: str,
    wallet: str,
    product: str,
    quantity: int,
    shippingzone: str,
    address: str,
    email: str,
    invoiceid: str,
    paid: bool,
    shipped: bool,
) -> Orders:
    returning = "" if db.type == SQLITE else "RETURNING ID"
    method = db.execute if db.type == SQLITE else db.fetchone

    order_id = urlsafe_short_hash()
    result = await (method)(
        f"""
            INSERT INTO diagonalley.orders (id, productid, wallet, product,
            quantity, shippingzone, address, email, invoiceid, paid, shipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            {returning}
            """,
        (
            order_id,
            productid,
            wallet,
            product,
            quantity,
            shippingzone,
            address,
            email,
            invoiceid,
            False,
            False,
        ),
    )
    if db.type == SQLITE:
        order_id = result._result_proxy.lastrowid
    else:
        order_id = result[0]

    link = await get_diagonalleys_order(order_id)
    assert link, "Newly created link couldn't be retrieved"
    return link


async def get_diagonalleys_order(order_id: str) -> Optional[Orders]:
    row = await db.fetchone("SELECT * FROM diagonalley.orders WHERE id = ?", (order_id,))
    return Orders.from_row(row) if row else None


async def get_diagonalleys_orders(wallet_ids: Union[str, List[str]]) -> List[Orders]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM diagonalley.orders WHERE wallet IN ({q})", (*wallet_ids,)
    )
    #
    return [Orders.from_row(row) for row in rows]


async def delete_diagonalleys_order(order_id: str) -> None:
    await db.execute("DELETE FROM diagonalley.orders WHERE id = ?", (order_id,))
