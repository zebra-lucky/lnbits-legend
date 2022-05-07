from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_payerinv")

payerinv_static_files = [
    {
        "path": "/payerinv/static",
        "app": StaticFiles(directory="lnbits/extensions/payerinv/static"),
        "name": "payerinv_static",
    }
]

payerinv_ext: APIRouter = APIRouter(prefix="/payerinv", tags=["payerinv"])


def payerinv_renderer():
    return template_renderer(["lnbits/extensions/payerinv/templates"])


from .views import *  # noqa
from .views_api import *  # noqa
