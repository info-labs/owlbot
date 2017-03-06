from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

import dns

from .. import context


class TestContext(TestCase):
    def setUp(self):
        self.context = context.Context("owlbot")

    def test_robots_txt_404(self):
        self.assertFalse(self.context.has_robots_txt("example.com"))
        self.context.register_robots_txt("example.com", 404, b"")
        self.assertTrue(self.context.has_robots_txt("example.com"))

    def test_robots_txt_200_disallow(self):
        self.context.register_robots_txt("example.com", 200, b"User-Agent: *\r\nDisallow: /")
        self.assertTrue(self.context.has_robots_txt("example.com"))
        self.assertFalse(self.context.can_fetch("http://example.com/"))

    def test_robots_txt_200_allow(self):
        self.context.register_robots_txt("example.com", 200, b"User-Agent: *\r\nAllow: /")
        self.assertTrue(self.context.has_robots_txt("example.com"))
        self.assertTrue(self.context.can_fetch("http://example.com/"))

    @patch("dns.resolver.Resolver.query")
    def test_resolve_dns(self, query):
        self.init_dns(query)
        cache = self.context.resolve_dns("example.com")
        self.assertEqual(len(cache.answers), 1)
        self.assertEqual(cache.answers[0].ttl, 38000)

    @patch("dns.resolver.Resolver.query")
    def test_check_ttl(self, query):
        self.init_dns(query)
        self.assertTrue(self.context.check_ttl("example.com"))
        self.context.resolve_dns("example.com")
        self.assertFalse(self.context.check_ttl("example.com"))

    def init_dns(self, query):
        """
        for dns.resolver.Resolver.query
        """
        rdata = MagicMock(
            rdtype=dns.rdatatype.A,
        )
        rdata.__str__.return_value = "93.184.216.34"
        rset = Mock(
            ttl=38000,
            items=[rdata],
        )
        rset.to_text.return_value = "example.com. 38000 IN A 93.184.216.34"
        query.return_value = Mock(
            response=Mock(
                answer=[rset],
            ),
        )
