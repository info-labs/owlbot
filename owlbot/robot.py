# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import requests

from . import context
from . import useragent


class Robot:
    def __init__(self, botname, comment=None):
        self.botname = botname
        self.comment = comment
        self.ctx = context.Context(self.botname)

    def register_robots_txt(self, host, code, content):
        self.ctx.register_robots_txt(host, code, content)

    @classmethod
    def create_robots_txt_url(cls, url):
        o = urlparse(url)
        return "http://{}/robots.txt".format(o.hostname)

    def can_fetch(self, url):
        o = urlparse(url)
        if not self.ctx.has_robots_txt(o.hostname):
            # not registered, see also register_robots_txt
            return None
        return self.ctx.can_fetch(url)

    def request(self, method, url, headers=None, data=None):
        if headers is None:
            headers = dict()
        headers = self.set_policy(headers)
        result = getattr(requests, method.lower())(url, headers=headers, data=data, stream=True)
        return result

    def get(self, url, headers=None, data=None):
        return self.request("GET", url, headers, data)

    def set_policy(self, headers):
        """
        set policy URL if not set
        :type headers: dict of (str, str)
        """
        headers = dict(headers)
        if "user-agent" not in set(x.lower() for x in headers.keys()):
            if self.comment is None:
                ua = useragent.UA_DEFAULT
            else:
                ua = useragent.UA_BASE.format(comment=" "+self.comment)
            headers["User-Agent"] = ua
        return headers
