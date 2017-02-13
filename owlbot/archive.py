# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from http.client import responses as RESPONSES
except ImportError:
    from httplib import responses as RESPONSES

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import io
import uuid

import warc

from . import robot
from . import useragent


def make_req_dummy(req, record):
    o = urlparse(req.url)
    path = o.path
    if not path:
        path = "/"
    temp = [
        bytes("{} {} HTTP/1.1".format(req.method, path), "ascii")
    ]
    for key in req.headers:
        temp.append(bytes("{}: {}".format(key, req.headers[key]), "utf-8"))
    temp.append(b"")
    if req.body:
        temp.append(req.body)
    dummy = b"\r\n".join(temp)
    header = warc.WARCHeader({
        "WARC-Type": "request",
        "WARC-Target-URI": req.url,
        # ISO 28500 Section 5.4 WARC-Date
        # > Multiple records written as part of a single capture event (see section 5.7)
        # > shall use the same WARC-Date, even though the times of their writing
        # > will not be exactly synchronized.
        "WARC-Date": record.header["WARC-Date"],
        "WARC-Concurrent-To": record.header["WARC-Record-ID"],
    }, defaults=True)
    return warc.WARCRecord(header, payload=dummy)


def make_resp_dummy(resp):
    body = resp.raw.read()
    temp = [
        bytes("HTTP/1.1 {} {}".format(resp.status_code, RESPONSES[resp.status_code]), "ascii"),
    ]
    applied_keys = []
    for key in resp.headers:
        if key.lower() in ["transfer-encoding"]:
            continue
        elif key.lower() == "content-length" and resp.headers["content-length"] != str(len(body)):
            # recalculate decoded size below
            continue
        temp.append(bytes("{}: {}".format(key, resp.headers[key]), "utf-8"))
        applied_keys.append(key.lower())
    if "content-length" not in applied_keys:
        temp.append(bytes("content-length: {}".format(len(body)), "ascii"))
    temp.append(b"")
    temp.append(body)
    dummy = b"\r\n".join(temp)
    header = warc.WARCHeader({
        "WARC-Type": "response",
        "WARC-Target-URI": resp.url,
    }, defaults=True)
    return warc.WARCRecord(header, payload=dummy)


make_req_record = make_req_dummy


def create(filename, fileobj=None, operator=None):
    """
    :rtype: warc.WARCFile
    """
    assert useragent.POLICY is not None

    if fileobj is None:
        fileobj = io.BytesIO()

    arc = warc.WARCFile(fileobj=fileobj)

    header = warc.WARCHeader({
        "WARC-Type": "warcinfo",
        "WARC-Filename": filename,
    })
    body = [
        b"software: owlbot/"+bytes(version.STR, "ascii"),
        b"format: WARC File Format 1.0",
        # policy from .OWLBOT_POLICY or os.environ["OWLBOT_POLICY"]
        b"robots: " + bytes(useragent.POLICY, "ascii"),
    ]
    if operator is not None:
        body.append(b"operator: " + operator.encode("utf-8"))

    arc.write_record(warc.WARCRecord(header, payload=b"\r\n".join(body)))

    return arc


def download(method, url, headers={}, data=None):
    """
    :type method: str
    :type url: str
    :type headers: dict of (str, str)
    :type data: bytes
    :rtype: int, warc.WARCRecord, warc.WARCRecord
    :return: status_code, response, request
    """
    resp = robot.download(method, url, headers, data)
    response = make_resp_dummy(resp)
    return resp.status_code, response, make_req_dummy(resp.request, response)
