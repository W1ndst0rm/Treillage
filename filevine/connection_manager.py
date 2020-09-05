import aiohttp
import asyncio
import functools
import time
from .token_manager import TokenManager
from .ratelimiter import RateLimiter
from .exceptions import FilevineHTTPException


def renew_access_token(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        if time.time() > self.token_manager.access_token_expiry:
            await self.token_manager.refresh_access_token()
        return await func(self, *args, **kwargs)

    return wrapped


def rate_limit(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        if self.rate_limiter:
            await self.rate_limiter.wait_for_token()
        return await func(self, *args, **kwargs)

    return wrapped


class ConnectionManager:
    def __init__(self,
                 base_url: str,
                 credentials: dict,
                 max_connections: int = None,
                 rate_limit_max_tokens: int = None,
                 rate_limit_token_regen_rate: int = None
                 ):
        self.__base_url = base_url
        self.__credentials = credentials
        if max_connections is not None:
            self.__connector = aiohttp.TCPConnector(limit_per_host=max_connections)
        else:
            self.__connector = None
        self.__session = None
        self.__token_manager = None
        if rate_limit_max_tokens is not None and rate_limit_token_regen_rate is not None:
            self.__rate_limiter = RateLimiter(rate_limit_max_tokens, rate_limit_token_regen_rate)
        else:
            self.__rate_limiter = None

    @classmethod
    async def create(cls,
                     base_url: str,
                     credentials: dict,
                     rate_limit_max_tokens: int = None,
                     rate_limit_token_regen_rate: int = None
                     ):

        self = ConnectionManager(base_url, credentials, rate_limit_max_tokens, rate_limit_token_regen_rate)
        self.__token_manager = await TokenManager.create(credentials, base_url)
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
            await asyncio.sleep(0.250)  # Sleep to give connections time to close

    @property
    def token_manager(self) -> TokenManager:
        return self.__token_manager

    @property
    def rate_limiter(self) -> RateLimiter:
        return self.__rate_limiter

    @property
    def connector(self) -> aiohttp.TCPConnector:
        return self.__connector

    @renew_access_token
    @rate_limit
    async def get(self, endpoint: str, params: dict = None, headers: dict = None):
        url = self.__base_url + endpoint
        if not headers:
            headers = dict()
        headers["x-fv-sessionid"] = self.token_manager.refresh_token
        headers["Authorization"] = f"Bearer {self.__token_manager.access_token}"
        async with self.__session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                msg = await response.text()
                raise FilevineHTTPException(code=response.status, url=url, msg=msg)

    @renew_access_token
    @rate_limit
    async def patch(self, endpoint: str, json: dict, headers: dict = None):
        url = self.__base_url + endpoint
        headers["x-fv-sessionid"] = self.token_manager.refresh_token
        headers["Authorization"] = f"Bearer {self.__token_manager.access_token}"
        async with self.__session.patch(url, json=json, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                msg = await response.text()
                raise FilevineHTTPException(code=response.status, url=url, msg=msg)

    @renew_access_token
    @rate_limit
    async def post(self, endpoint: str, json: dict, headers: dict = None):
        url = self.__base_url + endpoint
        headers["x-fv-sessionid"] = self.token_manager.refresh_token
        headers["Authorization"] = f"Bearer {self.__token_manager.access_token}"
        async with self.__session.post(url, json=json, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                msg = await response.text()
                raise FilevineHTTPException(code=response.status, url=url, msg=msg)
