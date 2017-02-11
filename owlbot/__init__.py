# -*- coding: utf-8 -*-

from . import archive
from . import useragent
from . import version


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


__author__ = 'mugwort_rc <mugwort.rc@gmail.com>'
__copyright__ = 'Copyright (c) mugwort_rc'
__description__ = 'WARC generator.'
__license__ = 'GPLv3'
__version__ = version.STR
