import datetime
from urllib.parse import urlparse

import dns.resolver

from .utility import robotparser


class Context:
    def __init__(self, botname):
        self.botname = botname
        self.resolver = dns.resolver.Resolver()
        self.dns_cache = {}
        self.robots_cache = {}

    def has_robots_txt(self, host):
        return host in self.robots_cache

    def register_robots_txt(self, host, code, content):
        self.robots_cache[host] = robotparser.RobotFileParser(code, content)

    def can_fetch(self, url):
        o = urlparse(url)
        robots = self.robots_cache[o.hostname]
        return robots.can_fetch(self.botname, url)

    def resolve_dns(self, host):
        """
        :rtype: bool, DNSCache
        :return: is_cache, dns response
        """
        if not self.check_ttl(host):
            return self.dns_cache[host]

        # resolve dns
        ans = self.resolver.query(host, "A")
        cache = DNSCache(ans.response.answer)
        self.dns_cache[host] = cache
        return cache

    def check_ttl(self, host):
        """
        :rtype: bool
        :return: is resolve require
        """
        if host not in self.dns_cache:
            # no cache
            return True

        now = datetime.datetime.utcnow()
        cache = self.dns_cache[host]
        answers = cache.answers
        # check TTL
        created_at = cache.created_at
        delta = now - created_at
        if all([(delta.seconds < x.ttl) for x in answers]):
            # can use cache
            return False

        # reached to TTL
        return True


class DNSCache:
    def __init__(self, answers, created_at=None):
        if created_at is None:
            created_at = datetime.datetime.utcnow()
        self.answers = answers
        self.created_at = created_at
