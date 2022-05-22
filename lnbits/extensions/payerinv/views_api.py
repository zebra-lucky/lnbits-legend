import asyncio
import time
from http import HTTPStatus

from fastapi import Request
from fastapi.param_functions import Query
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from lnbits import bolt11
from lnbits.core import db as core_db
from lnbits.core.crud import get_user
from lnbits.core.services import create_invoice, InvoiceFailure
from lnbits.decorators import WalletTypeInfo, get_key_type
from lnbits.utils.exchange_rates import (currencies, get_fiat_rate_satoshis,
    fiat_amount_as_satoshis)

from . import payerinv_ext
from .crud import (
    create_pay_link,
    delete_pay_link,
    get_pay_link,
    get_pay_links,
    update_pay_link,
)
from .models import CreatePayLinkData
from .image_captcha import generate_captcha, verify_captcha


@payerinv_ext.get("/api/v1/currencies")
async def api_list_currencies_available():
    return list(currencies.keys())


@payerinv_ext.get("/api/v1/links", status_code=HTTPStatus.OK)
async def api_links(
    req: Request,
    wallet: WalletTypeInfo = Depends(get_key_type),
    all_wallets: bool = Query(False),
):
    wallet_ids = [wallet.wallet.id]

    if all_wallets:
        wallet_ids = (await get_user(wallet.wallet.user)).wallet_ids

        return [
            {**link.dict(), "payerinv": link.payerinv_url(req)}
            for link in await get_pay_links(wallet_ids)
        ]


@payerinv_ext.get("/api/v1/links/{link_id}", status_code=HTTPStatus.OK)
async def api_link_retrieve(
    r: Request, link_id, wallet: WalletTypeInfo = Depends(get_key_type)
):
    link = await get_pay_link(link_id)

    if not link:
        raise HTTPException(
            detail="Pay link does not exist.", status_code=HTTPStatus.NOT_FOUND
        )

    if link.wallet != wallet.wallet.id:
        raise HTTPException(
            detail="Not your pay link.", status_code=HTTPStatus.FORBIDDEN
        )

    return {**link.dict(), **{"payerinv": link.payerinv_url(r)}}


@payerinv_ext.post("/api/v1/links", status_code=HTTPStatus.CREATED)
@payerinv_ext.put("/api/v1/links/{link_id}", status_code=HTTPStatus.OK)
async def api_link_create_or_update(
    data: CreatePayLinkData,
    link_id=None,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if data.min < 1:
        raise HTTPException(
            detail="Min must be more than 1.",
            status_code=HTTPStatus.BAD_REQUEST
        )

    if data.min > data.max:
        raise HTTPException(
            detail="Min is greater than max.",
            status_code=HTTPStatus.BAD_REQUEST
        )

    if data.currency == None and (
        round(data.min) != data.min or round(data.max) != data.max
    ):
        raise HTTPException(
            detail="Must use full satoshis.",
            status_code=HTTPStatus.BAD_REQUEST
        )

    if link_id:
        link = await get_pay_link(link_id)

        if not link:
            raise HTTPException(
                detail="Pay link does not exist.",
                status_code=HTTPStatus.NOT_FOUND
            )

        if link.wallet != wallet.wallet.id:
            raise HTTPException(
                detail="Not your pay link.",
                status_code=HTTPStatus.FORBIDDEN
            )

        link = await update_pay_link(**data.dict(), link_id=link_id)
    else:
        link = await create_pay_link(data, wallet_id=wallet.wallet.id)
    return {**link.dict(), "payerinv": link.payerinv_url}


@payerinv_ext.delete("/api/v1/links/{link_id}")
async def api_link_delete(
    link_id, wallet: WalletTypeInfo = Depends(get_key_type)
):
    link = await get_pay_link(link_id)

    if not link:
        raise HTTPException(
            detail="Pay link does not exist.", status_code=HTTPStatus.NOT_FOUND
        )

    if link.wallet != wallet.wallet.id:
        raise HTTPException(
            detail="Not your pay link.", status_code=HTTPStatus.FORBIDDEN
        )

    await delete_pay_link(link_id)
    raise HTTPException(status_code=HTTPStatus.NO_CONTENT)


@payerinv_ext.get("/api/v1/rate/{currency}", status_code=HTTPStatus.OK)
async def api_check_fiat_rate(currency):
    try:
        rate = await get_fiat_rate_satoshis(currency)
    except AssertionError:
        rate = None

    return {"rate": rate}


@payerinv_ext.post("/api/v1/captcha/", status_code=HTTPStatus.OK)
async def api_generate_captcha():
    captcha_uuid, captcha_b64 = generate_captcha()
    return {'captchaUuid': captcha_uuid, 'captchaB64': captcha_b64}


@payerinv_ext.post("/api/v1/captcha/{captcha_uuid}", status_code=HTTPStatus.OK)
async def api_check_captcha(captcha_uuid, captcha_guess):
    return verify_captcha(captcha_uuid, captcha_guess)


@payerinv_ext.post("/api/v1/links/{link_id}/inv", status_code=HTTPStatus.OK)
async def api_link_create_invoice(link_id, captcha_uuid, captcha_guess):
    link = await get_pay_link(link_id)
    if not link:
        raise HTTPException(
            detail="Pay link does not exist.", status_code=HTTPStatus.NOT_FOUND
        )

    if not verify_captcha(captcha_uuid, captcha_guess).get('correct'):
        raise HTTPException(
            detail="Captcha guess failed", status_code=503
        )

    if link.currency:
        amount = await fiat_amount_as_satoshis(link.max, link.currency)
    else:
        amount = int(link.max)

    async with core_db.connect() as conn:
        try:
            payment_hash, payment_request = await create_invoice(
                wallet_id=link.wallet,
                amount=amount,
                memo=link.description,
                description_hash=b"",
                conn=conn
            )
        except InvoiceFailure as e:
            raise HTTPException(status_code=520, detail=str(e))
        except Exception as exc:
            raise exc
    inv = bolt11.decode(payment_request)
    return {
        'invoice': {
            'bolt11': payment_request,
            'amount': inv.amount_msat,
            'memo': inv.description,
            'time': inv.date,
            'expiry': inv.expiry,
            'payment_hash': inv.payment_hash,
        }
    }
