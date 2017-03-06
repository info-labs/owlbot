import gzip
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from .. import response


class TestWrapper(TestCase):
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

    def test_links(self):
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.links(), [
            "http://example.com/style.css",
            "http://example.com/script.js",
            "http://example.com/image.png",
        ])

    def test_host(self):
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.host, "example.com")

    def test_code(self):
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.code, 200)

    def test_content(self):
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, self.content)

    def test_content_with_gzip(self):
        self.resp.headers["Content-Encoding"] = "gzip"
        self.resp.raw.data = gzip.compress(b"value")
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, b"value")

    def test_content_with_compress(self):
        self.resp.headers["Content-Encoding"] = "compress"  # LZW
        self.resp.raw.data = b"errorvalue"
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, b"")  # unsupported now

    def test_content_with_deflate(self):
        self.resp.headers["Content-Encoding"] = "deflate"
        self.resp.raw.data = b"errorvalue"
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, b"")  # unsupported now

    def test_content_with_identity(self):
        self.resp.headers["Content-Encoding"] = "identity"
        self.resp.raw.data = b"value"
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, b"value")

    def test_content_with_compress(self):
        self.resp.headers["Content-Encoding"] = "br"  # Brotli
        self.resp.raw.data = b"errorvalue"
        resp = response.ResponseWrapper(self.resp)
        self.assertEqual(resp.content, b"")  # unsupported now
