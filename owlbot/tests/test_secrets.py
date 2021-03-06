"""Test the secrets module.

As most of the functions in secrets are thin wrappers around functions
defined elsewhere, we don't need to test them exhaustively.
"""


from ..pep506 import secrets
import unittest
import string

# For Python 2/3 compatibility.
try:
    unicode
except NameError:
    # Python 3.
    unicode = str


# === Unit tests ===

class Compare_Digest_Tests(unittest.TestCase):
    """Test secrets.compare_digest function."""

    def test_equal(self):
        # Test compare_digest functionality with equal strings.
        for s in ("a", "bcd", "xyz123"):
            a = s*100
            b = s*100
            self.assertTrue(secrets.compare_digest(a, b))

    def test_unequal(self):
        # Test compare_digest functionality with unequal strings.
        self.assertFalse(secrets.compare_digest("abc", "abcd"))
        for s in ("x", "mn", "a1b2c3"):
            a = s*100 + "q"
            b = s*100 + "k"
            self.assertFalse(secrets.compare_digest(a, b))

    def test_bad_types(self):
        # Test that compare_digest raises with mixed types.
        a = "abcde"  # str in Python3, bytes in Python2.
        a = a.encode('ascii')
        assert isinstance(a, bytes)
        b = a.decode('ascii')
        assert isinstance(b, unicode)
        self.assertRaises(TypeError, secrets.compare_digest, a, b)
        self.assertRaises(TypeError, secrets.compare_digest, b, a)

    def test_bool(self):
        # Test that compare_digest returns a bool.
        self.assertTrue(isinstance(secrets.compare_digest("abc", "abc"), bool))
        self.assertTrue(isinstance(secrets.compare_digest("abc", "xyz"), bool))


class Random_Tests(unittest.TestCase):
    """Test wrappers around SystemRandom methods."""

    def test_randbits(self):
        # Test randbits.
        errmsg = "randbits(%d) returned %d"
        for numbits in (3, 12, 30):
            for i in range(6):
                n = secrets.randbits(numbits)
                self.assertTrue(0 <= n < 2**numbits, errmsg % (numbits, n))

    def test_choice(self):
        # Test choice.
        items = [1, 2, 4, 8, 16, 32, 64]
        for i in range(10):
            self.assertTrue(secrets.choice(items) in items)

    def test_randbelow(self):
        # Test randbelow.
        errmsg = "randbelow(%d) returned %d"
        for i in range(2, 10):
            n = secrets.randbelow(i)
            self.assertTrue(n in range(i), errmsg % (i, n))
        self.assertRaises(ValueError, secrets.randbelow, 0)


class Token_Tests(unittest.TestCase):
    """Test token functions."""

    def test_token_defaults(self):
        # Test that token_* functions handle default size correctly.
        for func in (secrets.token_bytes, secrets.token_hex,
                     secrets.token_urlsafe):
            name = func.__name__
            try:
                func()
            except TypeError:
                self.fail("%s cannot be called with no argument" % name)
            try:
                func(None)
            except TypeError:
                self.fail("%s cannot be called with None" % name)
        size = secrets.DEFAULT_ENTROPY
        self.assertEqual(len(secrets.token_bytes(None)), size)
        self.assertEqual(len(secrets.token_hex(None)), 2*size)

    def test_token_bytes(self):
        # Test token_bytes.
        self.assertTrue(isinstance(secrets.token_bytes(11), bytes))
        for n in (1, 8, 17, 100):
            self.assertEqual(len(secrets.token_bytes(n)), n)

    def test_token_hex(self):
        # Test token_hex.
        self.assertTrue(isinstance(secrets.token_hex(7), unicode))
        for n in (1, 12, 25, 90):
            s = secrets.token_hex(n)
            self.assertEqual(len(s), 2*n)
            self.assertTrue(all(c in string.hexdigits for c in s))

    def test_token_urlsafe(self):
        # Test token_urlsafe.
        self.assertTrue(isinstance(secrets.token_urlsafe(9), unicode))
        legal = string.ascii_letters + string.digits + '-_'
        for n in (1, 11, 28, 76):
            self.assertTrue(all(c in legal for c in secrets.token_urlsafe(n)))


if __name__ == '__main__':
    unittest.main()
