import datetime
import re
import gzip

from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

import dns

from .. import archive
from .. import version


class TestArchive(TestCase):
    def test_create(self):
        arc = archive.Archive(filename="test.warc")
        arc.fileobj.seek(0)
        for record in arc.warc:
            break
        self.assertEqual(record["WARC-Filename"], "test.warc")

    @patch("dns.resolver.Resolver.query")
    @patch("requests.api.request")
    def test_get(self, request, query):
        self.init_requests(request)
        self.init_dns(query)
        arc = archive.Archive(filename="test.warc")
        resp = arc.get("http://example.com/")
        self.assertEqual(query.called, True)
        self.assertEqual(query.call_count, 1)
        self.assertEqual(request.called, True)
        self.assertEqual(request.call_count, 2)
        arc.fileobj.seek(0)
        for i, record in enumerate(arc.warc, 1):
            pass
        self.assertEqual(i, 6)  # warcinfo, dns, robots(GET, REQ), (GET, REQ)

    @patch("dns.resolver.Resolver.query")
    def test_resolve_dns(self, query):
        self.init_dns(query)
        arc = archive.Archive(filename="test.warc")
        date = datetime.datetime.now()
        resp = arc.resolve_dns("example.com", date)
        self.assertEqual(query.called, True)
        self.assertEqual(query.call_count, 1)
        self.assertEqual(resp, "93.184.216.34")
        arc.fileobj.seek(0)
        for i, record in enumerate(arc.warc):
            if i > 0:
                # skip warcinfo
                break
        payload = record.payload.read()
        self.assertTrue(re.match("^\d{14}$", str(payload[:payload.index(b"\r\n")], "ascii")))
        self.assertEqual(
            payload[payload.index(b"\r\n")+2:],
            b"example.com. 38000 IN A 93.184.216.34"
        )

    def init_requests(self, request):
        """
        for requests.api.request
        """
        request.return_value = Mock(
            raw=Mock(version=11, data=b""),
            status_code=200,
            headers=[],
            request=Mock(url="http://example.com/", headers={}, body=""),
        )

    def init_dns(self, query):
        """
        for dns.resolver.Resolver.query
        """
        rdata = MagicMock(
            rdtype=dns.rdatatype.A,
        )
        rdata.__str__.return_value = "93.184.216.34"
        rset = Mock(
            ttl=38000,
            items=[rdata],
        )
        rset.to_text.return_value = "example.com. 38000 IN A 93.184.216.34"
        query.return_value = Mock(
            response=Mock(
                answer=[rset],
            ),
        )


class TestDummy(TestCase):
    def setUp(self):
        self.content = b"""
<html>
<head>
<link type="stylesheet" href="style.css"/>
<script src="script.js"></script>
</head>
<body>
<img src="image.png" alt="image"/>
</body>
</html>
"""
        self.resp = Mock(
            status_code=200,
            headers={
                "Content-Type": "text/html",
            },
            url="http://example.com/",
            raw=Mock(
                data=self.content
            ),
        )
        self.req = Mock(
            method="GET",
            url="http://example.com/",
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; owlbot/{} +http://example.com)".format(version.STR),
            },
            body=b"",
        )

    def test_make_resp_dummy(self):
        date = datetime.datetime.utcnow()
        resp = archive.make_resp_dummy(self.resp, date)
        payload = resp.payload.read()
        self.assertEqual(payload, b"\r\n".join([
            b"HTTP/1.1 200 OK",
            b"Content-Type: text/html",
            bytes("content-length: {}".format(len(self.content)), "ascii"),
            b"",
            self.content,
        ]))

    def test_make_req_dummy(self):
        date = datetime.datetime.utcnow()
        resp = archive.make_resp_dummy(self.resp, date)
        req = archive.make_req_dummy(self.req, resp)
        payload = req.payload.read()
        self.assertEqual(payload, b"\r\n".join([
            b"GET / HTTP/1.1",
            bytes("User-Agent: Mozilla/5.0 (compatible; owlbot/{} +http://example.com)".format(version.STR), "ascii"),
            b"",
        ]))
