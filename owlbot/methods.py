from . import archive
from . import useragent


def set_policy(headers):
    """
    set policy URL if not set
    :type headers: dict of (str, str)
    """
    if "user-agent" not in set(x.lower() for x in headers.keys()):
        if comment is None:
            ua = useragent.UA_DEFAULT
        else:
            ua = useragent.UA_BASE.format(comment=" "+comment)
        headers["User-Agent"] = ua
    return headers


def get(url, headers={}, comment=None):
    """
    :type url: str
    :type headers: dict of (str, str)
    :type comment: str
    :rtype: int, warc.WARCRecord, warc.WARCRecord
    :return: status_code, response, request
    """
    headers = set_policy(headers)
    # create response and request record
    return archive.download("GET", url, headers)
