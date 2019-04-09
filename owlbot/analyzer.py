import gzip
import os
import re

from lxml import html

from .utility.url import urlparse


def extract_document_link(url, content):
    """
    :type content: str
    :rtype: list of str
    """
    if not content:
        return []

    dom = html.fromstring(content)
    link_hrefs = dom.xpath("//link[@rel='stylesheet']/@href") + dom.xpath("//link[@rel='preload']/@href")
    script_srcs = dom.xpath("//script/@src")
    img_srcs = dom.xpath("//img/@src")
    frame_srcs = dom.xpath("//frame/@src")
    return resolve_document_links(
        url,
        map(str, link_hrefs + script_srcs + img_srcs + frame_srcs)
    )

def extract_follow_link(url, content):
    """
    :type content: str
    :rtype: list of str
    """
    if not content:
        return []

    dom = html.fromstring(content)
    a_hrefs = dom.xpath("//a/@href")
    return resolve_document_links(
        url,
        map(str, a_hrefs)
    )

RE_SCHEME = re.compile("^(\w+):.+")

def resolve_document_links(url, paths):
    o1 = urlparse(url)
    result = []
    for path in paths:
        m = RE_SCHEME.match(path)
        if m and m.group(1) not in ["http", "https"]:
            # javascript, about, chrome etc...
            continue
        if path.startswith("http://") or path.startswith("https://"):
            result.append(path)
            continue
        if path.startswith("//") and not path.startswith("///"):
            result.append(o1.scheme + ":" + os.path.normpath(path))
        else:
            path = resolve_path(o1.path, path)
            result.append(o1.scheme + "://" + o1.netloc + path)
    return result


def resolve_path(path1, path2):
    path1 = path1.strip()
    path2 = path2.strip()
    if "#" in path2:
        path2 = path2.split("#")[0]
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
