from http import HTTPStatus

from fastapi import Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists

from . import payerinv_ext, payerinv_renderer
from .crud import get_pay_link
from .image_captcha import generate_captcha

templates = Jinja2Templates(directory="templates")


@payerinv_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return payerinv_renderer().TemplateResponse(
        "payerinv/index.html", {"request": request, "user": user.dict()}
    )


@payerinv_ext.get("/{link_id}", name="payerinv.api_payerinv_response",
                  response_class=HTMLResponse)
async def display(request: Request, link_id):
    link = await get_pay_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Pay link does not exist."
        )
    captcha_uuid, captcha_b64 = generate_captcha()
    ctx = {
        'request': request,
        'payerinv': {
            'id': link.id,
            'amount': link.max,
            'currency': link.currency,
            'description': link.description,
            'captcha_uuid': captcha_uuid,
            'captcha_b64': captcha_b64,
        }
    }
    return payerinv_renderer().TemplateResponse("payerinv/display.html", ctx)
