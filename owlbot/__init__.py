# -*- coding: utf-8 -*-

from . import archive
from . import useragent


def get(url, headers={}):
    if "user-agent" not in set(x.lower() for x in headers.keys()):
        headers["user-agent"] = useragent.UA_DEFAULT
    return archive.download("GET", url, headers)
