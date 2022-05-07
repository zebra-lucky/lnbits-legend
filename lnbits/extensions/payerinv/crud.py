from typing import List, Optional, Union

from lnbits.db import SQLITE
from . import db
from .models import PayLink, CreatePayLinkData


async def create_pay_link(data: CreatePayLinkData, wallet_id: str) -> PayLink:

    returning = "" if db.type == SQLITE else "RETURNING ID"
    method = db.execute if db.type == SQLITE else db.fetchone
    result = await (method)(
        f"""
        INSERT INTO payerinv.pay_links (
            wallet,
            description,
            currency,
            min,
            max
        )
        VALUES (?, ?, ?, ?, ?)
        {returning}
        """,
        (
            wallet_id,
            data.description,
            data.currency,
            data.min,
            data.max,
        ),
    )
    if db.type == SQLITE:
        link_id = result._result_proxy.lastrowid
    else:
        link_id = result[0]

    link = await get_pay_link(link_id)
    assert link, "Newly created link couldn't be retrieved"
    return link


async def get_pay_link(link_id: int) -> Optional[PayLink]:
    row = await db.fetchone("SELECT * FROM payerinv.pay_links WHERE id = ?",
                            (link_id,))
    return PayLink.from_row(row) if row else None


async def get_pay_links(wallet_ids: Union[str, List[str]]) -> List[PayLink]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"""
        SELECT * FROM payerinv.pay_links WHERE wallet IN ({q})
        ORDER BY Id
        """,
        (*wallet_ids,),
    )
    return [PayLink.from_row(row) for row in rows]


async def update_pay_link(link_id: int, **kwargs) -> Optional[PayLink]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE payerinv.pay_links SET {q} WHERE id = ?",
        (*kwargs.values(), link_id)
    )
    row = await db.fetchone("SELECT * FROM payerinv.pay_links WHERE id = ?",
                            (link_id,))
    return PayLink.from_row(row) if row else None


async def delete_pay_link(link_id: int) -> None:
    await db.execute("DELETE FROM payerinv.pay_links WHERE id = ?", (link_id,))
