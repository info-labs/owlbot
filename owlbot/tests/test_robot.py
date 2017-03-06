from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from .. import robot
from .. import version


class TestRobot(TestCase):
    def setUp(self):
        self.robot = robot.Robot("owlbot")

    def test_robots_txt_200_disallow(self):
        self.robot.register_robots_txt("example.com", 200, b"User-Agent: *\r\nDisallow: /")
        self.assertFalse(self.robot.can_fetch("http://example.com/"))

    def test_robots_txt_200_allow(self):
        self.robot.register_robots_txt("example.com", 200, b"User-Agent: *\r\nAllow: /")
        self.assertTrue(self.robot.can_fetch("http://example.com/"))

    @patch("requests.api.request")
    def test_request(self, request):
        self.init_requests(request)
        resp = self.robot.request("GET", "http://example.com/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.request.url, "http://example.com/")

    @patch("owlbot.robot.Robot.request")
    def test_get(self, request):
        resp = self.robot.get("http://example.com/")
        self.assertTrue(request.called)
        self.assertTrue(request.called_with("GET", "http://example.com/", None, None))
        self.assertEqual(request.call_count, 1)

    def test_set_policy(self):
        test = {}
        self.assertEqual(self.robot.set_policy(test), {"User-Agent": "Mozilla/5.0 (compatible; owlbot/{} +http://example.com)".format(version.STR)})
        self.assertEqual(test, {})

    def init_requests(self, request):
        """
        for requests.api.request
        """
        request.return_value = Mock(
            raw=Mock(version=11, data=b""),
            status_code=200,
            headers=[],
            request=Mock(url="http://example.com/", headers={}, body=""),
        )
