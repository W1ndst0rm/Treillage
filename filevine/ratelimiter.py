import asyncio
import time


class RateLimiter:
    def __init__(self, token_count=10, token_rate=10):
        self.__tokens = token_count
        self.__MAX_TOKENS = token_count
        self.__token_rate = token_rate
        self.__last_update = time.monotonic()

    async def wait_for_token(self):
        while self.__tokens <= 1:
            self.__add_new_token()
            await asyncio.sleep(1)
        self.__tokens -= 1

    @property
    def tokens(self) -> int:
        return self.__tokens

    @tokens.setter
    def tokens(self, i):
        self.__tokens = min(i, self.__MAX_TOKENS)

    def __add_new_token(self):
        now = time.monotonic()
        time_since_update = now - self.__last_update
        new_tokens = time_since_update * self.__token_rate
        if self.__tokens + new_tokens >= 1:
            self.tokens += new_tokens  # = min(self.__tokens + new_tokens, self.__MAX_TOKENS)
            self.__last_update = now
