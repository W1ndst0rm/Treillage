import aiohttp
import asyncio
import functools
import time
from .token_manager import TokenManager
from .ratelimiter import RateLimiter
from .exceptions import TreillageHTTPException, TreillageRateLimitException


def renew_access_token(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        # Refresh the token 90 seconds before it expires
        if time.time() > self.token_manager.access_token_expiry - 90:
            await self.token_manager.refresh_access_token()
        return await func(self, *args, **kwargs)

    return wrapped


def rate_limit(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        if self.rate_limiter:
            await self.rate_limiter.get_token()
        return await func(self, *args, **kwargs)

    return wrapped


def retry_on_rate_limit(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        while True:
            try:
                return await func(self, *args, **kwargs)
            except TreillageRateLimitException:
                pass
    return wrapped


class ConnectionManager:
    def __init__(self,
                 base_url: str,
                 credentials,
                 max_connections: int = None,
                 rate_limit_token_regen_rate: int = None
                 ):
        self.__base_url = base_url
        self.__credentials = credentials
        if max_connections is not None:
            self.__connector = aiohttp.TCPConnector(
                limit_per_host=max_connections
            )
        else:
            self.__connector = None
        self.__session = None
        self.__auth_tokens = None
        if rate_limit_token_regen_rate is not None:
            self.__rate_limiter = RateLimiter(
                token_rate=rate_limit_token_regen_rate
            )
        else:
            self.__rate_limiter = None

    @classmethod
    async def create(cls,
                     base_url: str,
                     credentials,
                     max_connections: int = None,
                     rate_limit_token_regen_rate: int = None
                     ):

        self = ConnectionManager(
            base_url,
            credentials,
            max_connections,
            rate_limit_token_regen_rate
        )
        self.__auth_tokens = await TokenManager.create(credentials, base_url)
        if self.connector:
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=90),
                connector=self.connector
            )
        else:
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=90)
            )
        return self

    async def close(self):
        if self.__session is not None:
            await self.__session.close()
            # Sleep to give connections time to close
            await asyncio.sleep(0.250)

    @property
    def token_manager(self) -> TokenManager:
        return self.__auth_tokens

    @property
    def rate_limiter(self) -> RateLimiter:
        return self.__rate_limiter

    @property
    def connector(self) -> aiohttp.TCPConnector:
        return self.__connector

    async def __handle_response(self, response, http_success_code: int = 200):
        if response.status == http_success_code:
            if self.__rate_limiter is not None:
                self.__rate_limiter.last_try_success(True)
            return await response.json()
        else:
            msg = await response.text()
            if response.status == 429:
                if self.__rate_limiter is not None:
                    self.__rate_limiter.last_try_success(False)
                raise TreillageRateLimitException(url=response.url, msg=msg)
            else:
                raise TreillageHTTPException(
                    code=response.status,
                    url=response.url,
                    msg=msg
                )

    def __setup_headers(self, headers: dict = None) -> dict:
        if not headers:
            headers = dict()
        headers["x-fv-sessionid"] = self.__auth_tokens.refresh_token
        headers["Authorization"] = f"Bearer {self.__auth_tokens.access_token}"
        return headers

    @renew_access_token
    @rate_limit
    async def get(
            self,
            endpoint: str,
            params: dict = None,
            headers: dict = None
    ):
        async with self.__session.get(
                url=self.__base_url + endpoint,
                params=params,
                headers=self.__setup_headers(headers)
        ) as response:
            return await self.__handle_response(response, 200)

    @renew_access_token
    @rate_limit
    async def patch(self, endpoint: str, body: dict, headers: dict = None):
        async with self.__session.patch(
                url=self.__base_url + endpoint,
                body=body,
                headers=self.__setup_headers(headers)
        ) as response:
            return await self.__handle_response(response, 200)

    @renew_access_token
    @rate_limit
    async def post(self, endpoint: str, body: dict, headers: dict = None):
        async with self.__session.post(
                url=self.__base_url + endpoint,
                body=body,
                headers=self.__setup_headers(headers)
        ) as response:
            return await self.__handle_response(response, 200)

    @renew_access_token
    @rate_limit
    async def delete(self, endpoint: str, headers: dict = None):
        async with self.__session.delete(
                url=self.__base_url + endpoint,
                headers=self.__setup_headers(headers)
        ) as response:
            return await self.__handle_response(response, 204)
