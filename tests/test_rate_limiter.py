import asyncio
import time
import unittest
from treillage import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_create(self):
        rate = 10
        rl = RateLimiter(token_rate=rate)
        self.assertEqual(rate, rl.tokens)
        self.assertEqual(rate, rl._RateLimiter__MAX_TOKENS)
        self.assertEqual(rate, rl._RateLimiter__token_rate)

    def test_token_count_setter(self):
        rl = RateLimiter()
        self.assertEqual(8, rl.tokens)
        rl.tokens = 5
        self.assertEqual(5, rl.tokens)
        rl.tokens = 20
        self.assertEqual(8, rl.tokens)
        rl.tokens = -5
        self.assertEqual(0, rl.tokens)
        rl.tokens = 8
        self.assertEqual(8, rl.tokens)

    def test_add_new_token(self):
        rl = RateLimiter(token_rate=10)
        rl.tokens = 0
        rl._RateLimiter__last_update = time.monotonic()
        rl._RateLimiter__add_new_token()
        self.assertEqual(0, rl.tokens)
        time.sleep(.25)
        rl._RateLimiter__add_new_token()
        self.assertAlmostEqual(2.5, rl.tokens, delta=.2)
        time.sleep(.1)
        rl._RateLimiter__add_new_token()
        self.assertAlmostEqual(3.5, rl.tokens, delta=.2)
        time.sleep(1)
        rl._RateLimiter__add_new_token()
        self.assertEqual(10, rl.tokens)

    def test_get_token(self):
        rl = RateLimiter(token_rate=8)
        rl.tokens = 0
        start = time.monotonic()
        rl._RateLimiter__last_update = start
        asyncio.run(rl.get_token())
        end = time.monotonic()
        elapsed = end - start
        self.assertAlmostEqual(.125, elapsed, delta=.02)

    def test_backoff(self):
        rl = RateLimiter(token_rate=10)
        rl.tokens = 0
        rl.last_try_success(False)
        start = time.monotonic()
        rl._RateLimiter__last_update = start
        asyncio.run(rl.get_token())
        end = time.monotonic()
        elapsed = end - start
        self.assertGreater(
            elapsed,
            1 / rl._RateLimiter__token_rate
        )


if __name__ == '__main__':
    unittest.main()
