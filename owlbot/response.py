import gzip

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from . import analyzer


class ResponseWrapper:
    def __init__(self, resp):
        self.resp = resp

    def links(self):
        content_type = self.resp.headers["Content-Type"]
        if not content_type.startswith("text/html") and not content_type.startswith("application/xhtml"):
            return []
        return analyzer.extract_document_link(self.resp.url, self.content)

    @property
    def host(self):
        o = urlparse(self.resp.url)
        return o.hostname

    @property
    def url(self):
        return self.resp.url

    @property
    def code(self):
        return self.resp.status_code

    @property
    def content_type(self):
        return self.resp.headers["Content-Type"]

    @property
    def content(self):
        if self.resp.status_code != 200:
            return b""

        if "Content-Type" not in self.resp.headers:
            return b""

        text = self.resp.raw.data

        if "Content-Encoding" in self.resp.headers:
            encoding = self.resp.headers["Content-Encoding"]
            if encoding not in ["gzip", "identity"]:
                return b""
            if encoding == "gzip":
                try:
                    return gzip.decompress(text)
                except OSError:
                    # unknown decode error
                    return b""
            elif encoding == "identity":
                return text
            else:
                return b""
        return text
