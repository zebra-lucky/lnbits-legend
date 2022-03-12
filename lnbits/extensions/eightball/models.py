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

game_counters: Dict = {}


class gameCounter:
    wordlist: List[str]
    fulfilled_payments: OrderedDict
    counter: int

    @classmethod
    def invoke(cls, game: "game"):
        game_counter = game_counters.get(game.id)
        if not game_counter:
            game_counter = cls(wordlist=game.wordlist.split("\n"))
            game_counters[game.id] = game_counter
        return game_counter

    @classmethod
    def reset(cls, game: "game"):
        game_counter = cls.invoke(game)
        game_counter.counter = -1
        game_counter.wordlist = game.wordlist.split("\n")

    def __init__(self, wordlist: List[str]):
        self.wordlist = wordlist
        self.fulfilled_payments = OrderedDict()
        self.counter = -1

    def get_word(self, payment_hash):
        if payment_hash in self.fulfilled_payments:
            return self.fulfilled_payments[payment_hash]

        # get a new word
        self.counter += 1
        word = self.wordlist[self.counter % len(self.wordlist)]
        self.fulfilled_payments[payment_hash] = word

        # cleanup confirmation words cache
        to_remove = len(self.fulfilled_payments) - 23
        if to_remove > 0:
            for i in range(to_remove):
                self.fulfilled_payments.popitem(False)

        return word


class game(BaseModel):
    id: int
    name: str
    description: str
    wallet: str
    image: Optional[str]
    enabled: bool
    price: int
    unit: str
    wordlist: str

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
        self, wordlist: wordlist, payment_hash: str, req: Request
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
