# -*- coding: utf-8 -*-

from . import archive
from . import useragent


def get(url, headers={}, comment=None):
    """
    :type url: str
    :type headers: dict of (str, str)
    :type comment: str
    """
    if "user-agent" not in set(x.lower() for x in headers.keys()):
        if comment is None:
            ua = useragent.UA_DEFAULT
        else:
            ua = useragent.UA_BASE.format(comment=" "+comment)
        headers["user-agent"] = ua
    return archive.download("GET", url, headers)
