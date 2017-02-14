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

import datetime
import io
import uuid

import warc

from . import analyzer
from . import context
from . import robot
from . import useragent
from . import version
from .pep506 import secrets


HTTP_VERSION = {
    10: "1.0",
    11: "1.1",
}


def make_req_dummy(req, record, date, http_ver="1.1"):
    o = urlparse(req.url)
    path = o.path
    if not path:
        path = "/"
    temp = [
        bytes("{} {} HTTP/{}".format(req.method, path, http_ver), "ascii")
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


def make_resp_dummy(resp, date, http_ver="1.1"):
    body = resp.raw.data
    temp = [
        bytes("HTTP/{} {} {}".format(http_ver, resp.status_code, RESPONSES[resp.status_code]), "ascii"),
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
        "WARC-Date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }, defaults=True)
    return warc.WARCRecord(header, payload=dummy)


make_req_record = make_req_dummy


class Archive:
    def __init__(self, filename, fileobj=None, operator=None):
        self.ctx = context.Context()
        self.create(filename, fileobj=fileobj, operator=operator)

    def create(self, filename, fileobj=None, operator=None):
        """
        :rtype: warc.WARCFile
        """
        assert useragent.POLICY is not None

        if fileobj is None:
            fileobj = io.BytesIO()

        self.fileobj = fileobj
        self.warc = warc.WARCFile(fileobj=fileobj)

        header = warc.WARCHeader({
            "WARC-Type": "warcinfo",
            "WARC-Filename": filename,
        }, defaults=True)
        body = [
            b"software: owlbot/"+bytes(version.STR, "ascii"),
            b"format: WARC File Format 1.0",
            # policy from .OWLBOT_POLICY or os.environ["OWLBOT_POLICY"]
            b"robots: " + bytes(useragent.POLICY, "ascii"),
        ]
        if operator is not None:
            body.append(b"operator: " + operator.encode("utf-8"))

        self.warc.write_record(
            warc.WARCRecord(header, payload=b"\r\n".join(body))
        )

    def resolve_dns(self, hostname, date):
        ttl = self.ctx.check_ttl(hostname)
        cache = self.ctx.resolve_dns(hostname)

        if ttl:
            header = warc.WARCHeader({
                "WARC-Type": "response",
                "WARC-Target-URI": "dns:{}".format(hostname),
                "WARC-Date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Content-Type": "text/dns",
            }, defaults=True)
            body = (
                # RFC 2540 section 2.2 Text Format
                [cache.created_at.strftime("%Y%m%d%H%M%S")]
                 + [x.to_text() for x in cache.answers]
            )
            record = warc.WARCRecord(header,
                                    payload=bytes("\r\n".join(body), "ascii"))
            self.warc.write_record(record)

        temp = []
        for anser in cache.answers:
            temp += [x for x in anser.items if x.rdtype == dns.rdatatype.A]
        return str(secrets.choice(temp))

    def request(self, method, url, headers={}, data=None):
        now = datetime.datetime.utcnow()

        o = urlparse(url)
        ip_addr = self.resolve_dns(o.hostname, date=now)

        # TODO: request with ip_addr
        resp = robot.request(method, url, headers, data)
        ver = HTTP_VERSION[resp.raw.version]
        response = make_resp_dummy(resp, date=now, http_ver=ver)
        request = make_req_dummy(resp.request, response, date=now, http_ver=ver)

        self.warc.write_record(response)
        self.warc.write_record(request)

        links = analyzer.extract_document_link(resp)

        return links

    def get(self, url, headers={}, comment=None):
        """
        :type url: str
        :type headers: dict of (str, str)
        :type comment: str
        :rtype: int, warc.WARCRecord, warc.WARCRecord
        :return: status_code, response, request
        """
        headers = self.set_policy(headers, comment=comment)
        # create response and request record
        return self.request("GET", url, headers)

    @classmethod
    def set_policy(cls, headers, comment):
        """
        set policy URL if not set
        :type headers: dict of (str, str)
        """
        if "user-agent" not in set(x.lower() for x in headers.keys()):
            if comment is None:
                ua = useragent.UA_DEFAULT
            else:
                ua = useragent.UA_BASE.format(comment=" "+comment)
            headers["User-Agent"] = ua
        return headers
