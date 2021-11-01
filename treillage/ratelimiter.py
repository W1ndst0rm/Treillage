import asyncio
from math import log2, ceil
import random
import time


class RateLimiter:
    def __init__(self,
                 token_rate: int = 8,
                 max_backoff_time: int = 64):
        self.__tokens = token_rate
        self.__MAX_TOKENS = token_rate
        self.__token_rate = token_rate
        self.__last_update = time.monotonic()
        self.__max_backoff_time = max_backoff_time
        self.__last_try_success = True
        self.__failed_attempts = 0

    async def get_token(self):
        # backoff if a rate limit error was received
        if self.__failed_attempts > 0:
            await asyncio.sleep(
                self.__get_backoff_time_ms() / 1000  # convert ms to seconds
            )
        # Regen tokens if there aren't any available
        while self.__tokens < 1:
            await self.__wait_for_token()
        # Consume a token
        self.__tokens -= 1

    async def __wait_for_token(self):
        # Check if there are any tokens available to regen
        if not self.__add_new_token():
            # If not wait the amount of time it take to regen one token
            await asyncio.sleep(1 / self.__token_rate)

    @property
    def tokens(self) -> int:
        return self.__tokens

    @tokens.setter
    def tokens(self, i):
        # Must be between 0 and MAX_TOKENS
        self.__tokens = max(min(i, self.__MAX_TOKENS), 0)

    def last_try_success(self, was_success: bool):
        self.__last_try_success = was_success
        if not was_success:
            self.__failed_attempts += 1
        else:
            self.__failed_attempts = max(
                0,
                self.__failed_attempts - self.__MAX_TOKENS / 3
            )

    def __get_backoff_time_ms(self) -> float:
        """
        Return time in milliseconds to backoff after a failed request

        Returns a random amount of time in milliseconds between 100ms and an
        upper limit of 2^num_failed_attempts * 100. To avoid overflow, the
        maximum exponent is limited so that max_backoff_time is never exceeded
        """
        return random.randint(
            100,  # minimum 100ms
            # The ceil function is working in tenths of seconds,
            # so max_backoff_time must be converted from seconds to tenths of
            # seconds and the result must be converted from tenths to
            # milliseconds (thousandths of seconds).
            ceil(2 ** (
                min(
                    log2(self.__max_backoff_time * 10),
                    self.__failed_attempts
                )
            )) * 100
        )

    def __add_new_token(self) -> bool:
        now = time.monotonic()
        time_since_update = now - self.__last_update
        new_tokens = time_since_update * self.__token_rate
        if self.__tokens + new_tokens >= 1:
            self.tokens += new_tokens
            self.__last_update = now
            return True
        else:
            return False
