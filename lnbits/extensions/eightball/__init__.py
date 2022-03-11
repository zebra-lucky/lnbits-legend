from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_eightball")

eightball_static_files = [
    {
        "path": "/eightball/static",
        "app": StaticFiles(directory="lnbits/extensions/eightball/static"),
        "name": "eightball_static",
    }
]

eightball_ext: APIRouter = APIRouter(prefix="/eightball", tags=["eightball"])


def eightball_renderer():
    return template_renderer(["lnbits/extensions/eightball/templates"])


from .lnurl import *  # noqa
from .views import *  # noqa
from .views_api import *  # noqa
