from . import analyzer
from .utility.url import urlparse


class CrawlRule:
    def __init__(self, domain="*"):
        self.domain = domain
        self.allow_follow_link = []

    def set_domain(self, netloc):
        self.domain = netloc.lower()

    def add_follow_path(self, path):
        self.allow_follow_link.append(path)

    def test(self, url):
        if self.domain == "*":
            return True
        ol = urlparse(url)
        if ol.netloc.lower() != self.domain:
            return False
        return True

    def test_follow(self, url):
        ol = urlparse(url)
        if self.domain != "*":
            if not self.test(url):
                return False
        if not self.allow_follow_link:
            return True
        test_path = ol.path
        for path in self.allow_follow_link:
            if test_path.startswith(path):
                return True
        return False

    def extract_links(self, resp):
        content_type = resp.content_type
        if not content_type.startswith("text/html") and not content_type.startswith("application/xhtml"):
            return
        # required
        for link in analyzer.extract_document_link(resp.url, resp.content):
            if not self.test(link):
                continue
            yield link
        # follow link
        for link in analyzer.extract_follow_link(resp.url, resp.content):
            if not self.test_follow(link):
                continue
            yield link
