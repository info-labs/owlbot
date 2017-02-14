import gzip

from lxml import html

from .utility import fake


def extract_document_link(resp):
    """
    :type resp: requests.models.Response
    :rtype: list of str
    """
    if resp.status_code != 200:
        return []

    assert resp.raw.data != b""

    if "Content-Type" not in resp.headers:
        return []
    if not resp.headers["Content-Type"].startswith("text/html"):
        return []

    text = resp.raw.data
    if "Content-Encoding" in resp.headers:
        encoding = resp.headers["Content-Encoding"]
        if encoding not in ["gzip"]:
            return []
        if encoding == "gzip":
            try:
                text = gzip.decompress(text)
            except:
                # unknown decode error
                return []

    dom = html.fromstring(text)
    link_hrefs = dom.xpath("//link/@href")
    script_srcs = dom.xpath("//script/@src")
    img_srcs = dom.xpath("//img/@src")
    return map(str, link_hrefs + script_srcs + img_srcs)
