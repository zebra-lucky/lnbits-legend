from datetime import datetime
from typing import List, Optional, Union

from lnbits.db import open_ext_db
from lnbits.helpers import urlsafe_short_hash

from .models import WithdrawLink


def create_withdraw_link(
    *,
    wallet_id: str,
    title: str,
    min_withdrawable: int,
    max_withdrawable: int,
    uses: int,
    wait_time: int,
    is_unique: bool,
) -> WithdrawLink:
    if is_unique:
        uniques = ""
        for i in range(uses):
            uniques += "," + urlsafe_short_hash()
        uniques = uniques[1:]
    else:
        uniques = urlsafe_short_hash()

    with open_ext_db("withdraw") as db:
        link_id = urlsafe_short_hash()
        db.execute(
            """
            INSERT INTO withdraw_links (
                id,
                wallet,
                title,
                min_withdrawable,
                max_withdrawable,
                uses,
                wait_time,
                is_unique,
                unique_hash,
                k1,
                open_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                link_id,
                wallet_id,
                title,
                min_withdrawable,
                max_withdrawable,
                uses,
                wait_time,
                int(is_unique),
                uniques,
                urlsafe_short_hash(),
                int(datetime.now().timestamp()) + wait_time,
            ),
        )

    return get_withdraw_link(link_id, 0)


def get_withdraw_link(link_id: str, unique_hash_int: int) -> Optional[WithdrawLink]:
    with open_ext_db("withdraw") as db:
        row = db.fetchone("SELECT * FROM withdraw_links WHERE id = ?", (link_id,))
    withdraw = WithdrawLink.from_row(row) if row else None
    if row["is_unique"] == 0:
        return withdraw
    if withdraw == None:
        return withdraw
    link = []
    for item in row:
        link.append(item) 
    hashes = link[8].split(",")
    link[8] = hashes[unique_hash_int]
    print(link[8])
    print(unique_hash_int)
    return WithdrawLink._make(link)

def get_withdraw_link_by_hash(unique_hash: str) -> Optional[WithdrawLink]:
    with open_ext_db("withdraw") as db:
        row = db.fetchone("SELECT * FROM withdraw_links WHERE unique_hash LIKE = ?", (unique_hash,))

    return WithdrawLink.from_row(row) if row else None



def get_withdraw_links(wallet_ids: Union[str, List[str]]) -> List[WithdrawLink]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    with open_ext_db("withdraw") as db:
        q = ",".join(["?"] * len(wallet_ids))
        rows = db.fetchall(f"SELECT * FROM withdraw_links WHERE wallet IN ({q})", (*wallet_ids,))

    return [WithdrawLink.from_row(row) for row in rows]

def update_withdraw_link(link_id: str, **kwargs) -> Optional[WithdrawLink]:
    
    with open_ext_db("withdraw") as db:
        row = db.fetchone("SELECT * FROM withdraw_links WHERE id = ?", (link_id,))
    if kwargs["uses"] != row["uses"] or kwargs["is_unique"] == True and row["is_unique"] == False:
        uniques = ""
        for i in range(kwargs["uses"]):
            uniques += "," + urlsafe_short_hash()
            uniques = uniques[1:]
            kwargs.update( {'unique_hash' : uniques} )
            print(kwargs["unique_hash"])
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    with open_ext_db("withdraw") as db:
        db.execute(f"UPDATE withdraw_links SET {q} WHERE id = ?", (*kwargs.values(), link_id))
        row = db.fetchone("SELECT * FROM withdraw_links WHERE id = ?", (link_id,))

    return WithdrawLink.from_row(row) if row else None



def delete_withdraw_link(link_id: str) -> None:
    with open_ext_db("withdraw") as db:
        db.execute("DELETE FROM withdraw_links WHERE id = ?", (link_id,))
