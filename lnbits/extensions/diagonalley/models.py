import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, ParseResult
from quart import url_for
from typing import NamedTuple, Optional, Dict
from sqlite3 import Row
from lnbits.lnurl import encode as lnurl_encode  # type: ignore
from lnurl.types import LnurlPayMetadata  # type: ignore


class Indexers(NamedTuple):
    id: str
    wallet: str
    shopname: str
    indexeraddress: str
    online: bool
    rating: str
    shippingzone1: str
    shippingzone2: str
    zone1cost: int
    zone2cost: int
    email: str

    @classmethod
    def from_row(cls, row: Row) -> "Indexers":
        data = dict(row)
        return cls(**data)


class Products(NamedTuple):
    id: str
    wallet: str
    product: str
    categories: str
    description: str
    image: str
    price: int
    quantity: int

    @classmethod
    def from_row(cls, row: Row) -> "Products":
        data = dict(row)
        return cls(**data)


class Orders(NamedTuple):
    id: str
    productid: str
    wallet: str
    product: str
    quantity: int
    shippingzone: int
    address: str
    email: str
    invoiceid: str
    paid: bool
    shipped: bool

    @classmethod
    def from_row(cls, row: Row) -> "Orders":
        data = dict(row)
        return cls(**data)

