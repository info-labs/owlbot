import gzip

from lxml import html


def extract_document_link(content):
    """
    :type content: str
    :rtype: list of str
    """
    if not content:
        return []

    dom = html.fromstring(content)
    link_hrefs = dom.xpath("//link/@href")
    script_srcs = dom.xpath("//script/@src")
    img_srcs = dom.xpath("//img/@src")
    return map(str, link_hrefs + script_srcs + img_srcs)
