import asyncio
import time
import unittest
from treillage import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_create(self):
        rate = 10
        count = 20
        rl = RateLimiter(token_count=count, token_rate=rate)
        self.assertEqual(count, rl.tokens)
        self.assertEqual(count, rl._RateLimiter__MAX_TOKENS)
        self.assertEqual(rate, rl._RateLimiter__token_rate)

    def test_token_count_setter(self):
        rl = RateLimiter()
        self.assertEqual(10, rl.tokens)
        rl.tokens = 5
        self.assertEqual(5, rl.tokens)
        rl.tokens = 20
        self.assertEqual(10, rl.tokens)
        rl.tokens = -5
        self.assertEqual(0, rl.tokens)
        rl.tokens = 10
        self.assertEqual(10, rl.tokens)

    def test_add_new_token(self):
        rl = RateLimiter(token_rate=10)
        rl.tokens = 0
        rl._RateLimiter__last_update = time.monotonic()
        rl._RateLimiter__add_new_token()
        self.assertEqual(0, rl.tokens)
        time.sleep(.25)
        rl._RateLimiter__add_new_token()
        self.assertAlmostEqual(2.5, rl.tokens, delta=.11)
        time.sleep(.1)
        rl._RateLimiter__add_new_token()
        self.assertAlmostEqual(3.5, rl.tokens, delta=.11)
        time.sleep(1)
        rl._RateLimiter__add_new_token()
        self.assertEqual(10, rl.tokens)

    def test_wait_for_token(self):
        rl = RateLimiter(token_rate=10)
        rl.tokens = 0
        start = time.monotonic()
        rl._RateLimiter__last_update = start
        asyncio.run(rl.get_token())
        end = time.monotonic()
        elapsed = end - start
        self.assertAlmostEqual(.1, elapsed, delta=.02)

    def test_backoff(self):
        rl = RateLimiter(token_rate=10)
        rl.tokens = 0
        rl.last_try_success(False)
        start = time.monotonic()
        rl._RateLimiter__last_update = start
        asyncio.run(rl.get_token())
        end = time.monotonic()
        elapsed = end - start
        self.assertAlmostEqual(elapsed, 1/rl._RateLimiter__token_rate + rl._RateLimiter__backoff_time, delta=.025)


if __name__ == '__main__':
    unittest.main()
