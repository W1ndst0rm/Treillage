import asyncio
import random
import time


class RateLimiter:
    def __init__(self, token_count=10, token_rate=100):
        self.__tokens = token_count
        self.__MAX_TOKENS = token_count
        self.__token_rate = token_rate
        self.__last_update = time.monotonic()
        self.__last_try_success = True
        self.__backoff_time = 0
        self.__failed_attempts = 0

    async def wait_for_token(self):
        while self.__tokens <= 1:
            self.__add_new_token()
            await asyncio.sleep(1 + self.__backoff_time)
        self.__tokens -= 1

    @property
    def tokens(self) -> int:
        return self.__tokens

    @tokens.setter
    def tokens(self, i):
        self.__tokens = min(i, self.__MAX_TOKENS)

    def last_try_success(self, i: bool):
        self.__last_try_success = i
        if not i:
            self.__failed_attempts += 1
            self.__backoff_time = random.randint(0, min(32000, 100 * 2 ** self.__failed_attempts)) / 1000  # ms to s
        else:
            self.__failed_attempts = 0

    def __add_new_token(self):
        if not self.__last_try_success:
            now = time.monotonic()
            time_since_update = now - self.__last_update
            new_tokens = time_since_update * self.__token_rate
            if self.__tokens + new_tokens >= 1:
                self.tokens += new_tokens
                self.__last_update = now
        else:
            self.__last_update = time.monotonic()
