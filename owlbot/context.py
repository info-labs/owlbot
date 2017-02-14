import datetime

import dns.resolver


class Context:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.dns_cache = {}

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
