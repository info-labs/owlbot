import os
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import gzip

from lxml import html


def extract_document_link(url, content):
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
    return resolve_document_links(url,
                map(str, link_hrefs + script_srcs + img_srcs)
    )


def resolve_document_links(url, paths):
    o = urlparse(url)
    result = []
    for path in paths:
        if path.startswith("//") and not path.startswith("///"):
            result.append(o.scheme + ":" + os.path.normpath(path))
        else:
            path = resolve_path(o.path, path)
            result.append(o.scheme + "://" + o.netloc + path)
    return result


def resolve_path(path1, path2):
    path1 = path1.strip()
    path2 = path2.strip()
    if path2.startswith("/"):
        path = os.path.normpath(path2)
        if path.startswith("//"):
            return path[1:]
        return path
    if path1.endswith("/"):
        return os.path.normpath(os.path.join(path1, path2))
    else:
        base = ""
        if path1:
            base = path1[:path1.rindex("/")]
        return os.path.normpath(os.path.join(base, path2))
