from starlette.requests import Request
from fastapi.param_functions import Query
from typing import Optional
from sqlite3 import Row
from pydantic import BaseModel


class CreatePayLinkData(BaseModel):
    description: str
    currency: str = Query(None)
    min: int = Query(0.01, ge=0.01)
    max: int = Query(0.01, ge=0.01)


class PayLink(BaseModel):
    id: int
    wallet: str
    description: str
    currency: Optional[str]
    min: int
    max: int

    @classmethod
    def from_row(cls, row: Row) -> "PayLink":
        data = dict(row)
        return cls(**data)

    def payerinv_url(self, req: Request) -> str:
        url = req.url_for("payerinv.api_payerinv_response", link_id=self.id)
        return url
