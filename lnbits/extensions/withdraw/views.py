from flask import g, abort, render_template
from http import HTTPStatus

from lnbits.decorators import check_user_exists, validate_uuids

from lnbits.extensions.withdraw import withdraw_ext
from .crud import get_withdraw_link


@withdraw_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
def index():
    return render_template("withdraw/index.html", user=g.user)


@withdraw_ext.route("/<link_id>")
def display(link_id):
    link = get_withdraw_link(link_id, 0) or abort(HTTPStatus.NOT_FOUND, "Withdraw link does not exist.")

    return render_template("withdraw/display.html", link=link)


@withdraw_ext.route("/print/<link_id>")
def print_qr(link_id):
    links = []
    link = get_withdraw_link(link_id, 0) or abort(HTTPStatus.NOT_FOUND, "Withdraw link does not exist.")
    if link.is_unique == True:
        unique_hashs = link.unique_hash.split(",")
        count = 1
        for item in unique_hashs:
            links.append(get_withdraw_link(link_id, count))
            count + 1

    return render_template("withdraw/print_qr.html", link=link, unique=True, links=links)
