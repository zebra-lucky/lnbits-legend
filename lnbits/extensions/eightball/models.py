import json
import base64
import hashlib
from collections import OrderedDict

from typing import Optional, List, Dict
from lnurl import encode as lnurl_encode  # type: ignore
from lnurl.types import LnurlPayMetadata  # type: ignore
from lnurl.models import LnurlPaySuccessAction, UrlAction  # type: ignore
from pydantic import BaseModel
from starlette.requests import Request
from .helpers import totp


class game(BaseModel):
    id: int
    name: str
    description: str
    wallet: str
    image: Optional[str]
    enabled: bool
    price: int
    unit: str
    wordlist: List[str]

    def lnurl(self, req: Request) -> str:
        return lnurl_encode(req.url_for("eightball.lnurl_response", item_id=self.id))

    def values(self, req: Request):
        values = self.dict()
        values["lnurl"] = lnurl_encode(
            req.url_for("eightball.lnurl_response", item_id=self.id)
        )
        return values

    async def lnurlpay_metadata(self) -> LnurlPayMetadata:
        metadata = [["text/plain", self.description]]

        if self.image:
            metadata.append(self.image.split(":")[1].split(","))

        return LnurlPayMetadata(json.dumps(metadata))

    def success_action(
        self, wordlist: str, payment_hash: str, req: Request
    ) -> Optional[LnurlPaySuccessAction]:
        if not wordlist:
            return None

        return UrlAction(
            url=req.url_for("eightball.confirmation_code", p=payment_hash),
            description="Open to get the confirmation code for your purchase.",
        )

    def get_code(self, payment_hash: str) -> str:
        if self.method == "wordlist":
            sc = gameCounter.invoke(self)
            return sc.get_word(payment_hash)
        elif self.method == "totp":
            return totp(self.otp_key)
        return ""
