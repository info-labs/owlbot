from unittest import TestCase

from .. import analyzer


class TestAnalyzer(TestCase):
    def test_extract_document_link_link(self):
        links = analyzer.extract_document_link("http://example.com/path",
                    '<div><link type="stylesheet" href="/style.css"/></div>')
        self.assertEqual(links, ["http://example.com/style.css"])

    def test_extract_document_link_script(self):
        links = analyzer.extract_document_link("http://example.com/path",
                    '<div><script src="/script.js"></script></div>')
        self.assertEqual(links, ["http://example.com/script.js"])

    def test_extract_document_link_img(self):
        links = analyzer.extract_document_link("http://example.com/path",
                    '<div><img src="/image.png" alt="image"/></div>')
        self.assertEqual(links, ["http://example.com/image.png"])

    def test_resolve_document_links(self):
        links = analyzer.resolve_document_links("http://example.com/path/to", [
            "//example.com:443/hoge",
            "/hoge",
            "./hoge",
            "hoge",
            "../hoge"
        ])
        self.assertEquals(links, [
            "http://example.com:443/hoge",
            "http://example.com/hoge",
            "http://example.com/path/hoge",
            "http://example.com/path/hoge",
            "http://example.com/hoge",
        ])

    def test_resolve_path(self):
        self.assertEqual(
            analyzer.resolve_path("/path/to/", "./hoge"),
            "/path/to/hoge"
        )
        self.assertEqual(
            analyzer.resolve_path("/path/to", "./hoge"),
            "/path/hoge"
        )
        self.assertEqual(
            analyzer.resolve_path("/path/to", "/hoge"),
            "/hoge"
        )
        self.assertEqual(
            analyzer.resolve_path("/path/to", "//hoge"),
            "/hoge"
        )
        self.assertEqual(
            analyzer.resolve_path("/path/to", "///hoge"),
            "/hoge"
        )
