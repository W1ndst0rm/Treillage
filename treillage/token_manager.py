from aiohttp import ClientSession
import asyncio
from datetime import datetime
from enum import Enum
from .exceptions import TreillageHTTPException, TreillageException
import hashlib
import jwt


class TokenRequestType(Enum):
    KEY = 'key'
    SESSION = 'session'


class TokenManager:

    def __init__(self, credentials, base_url):
        self.__API_KEY = credentials.key
        self.__API_SECRET = credentials.secret
        self.__auth_url = '/'.join([base_url, "session"])
        self.__access_token = None
        self.__access_token_expiry = None
        self.__refresh_token = None
        self.__refresh_token_expiry = None
        self.__refresh_token_ttl = None
        self.__user_id = None
        self.__org_id = None

    @classmethod
    async def create(cls, credentials, base_url):
        self = TokenManager(credentials, base_url)
        self.__set_tokens(
            await self.__request_tokens(request_type=TokenRequestType.KEY)
        )
        return self

    @property
    def access_token(self) -> str:
        return self.__access_token

    @property
    def access_token_expiry(self) -> int:
        return self.__access_token_expiry

    @property
    def refresh_token(self) -> str:
        return self.__refresh_token

    @staticmethod
    def get_timestamp():
        timestamp = datetime.utcnow().isoformat()
        return timestamp[:-3] + 'Z'

    @staticmethod
    def create_hash(api_key, timestamp, api_secret):
        hash_string = '/'.join([api_key, timestamp, api_secret])
        return hashlib.md5(hash_string.encode()).hexdigest()

    async def __request_tokens(self, request_type: TokenRequestType):
        timestamp = self.get_timestamp()
        api_hash = self.create_hash(self.__API_KEY,
                                    timestamp,
                                    self.__API_SECRET)

        if request_type == TokenRequestType.KEY:
            request_body = {
                'mode': request_type.value,
                'apiKey': self.__API_KEY,
                'apiHash': api_hash,
                'apiTimestamp': timestamp,
            }
        elif request_type == TokenRequestType.SESSION:
            request_body = {
                'mode': request_type.value,
                'apiKey': self.__API_KEY,
                'apiHash': api_hash,
                'apiTimestamp': timestamp,
                'userId': self.__user_id,
                'orgId': self.__org_id,
                'sessionId': self.__refresh_token
            }
        else:
            raise TreillageException(msg="Invalid Token Request Type")
        try:
            async with ClientSession() as session:
                async with session.post(self.__auth_url,
                                        json=request_body) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        raise TreillageHTTPException(
                            resp.status,
                            msg='Failed to get API tokens',
                            url=self.__auth_url
                        )
        finally:
            await asyncio.sleep(0.250)

    def __set_tokens(self, tokens: dict):
        self.__access_token = tokens["accessToken"]
        self.__access_token_expiry = jwt.decode(jwt=tokens['accessToken'],
                                                algorithms=["RS256"],
                                                options={
                                                    "verify_signature": False,
                                                    "verify_aud": False,
                                                    "verify_iss": False
                                                }
                                                )['exp']
        self.__refresh_token = tokens["refreshToken"]
        self.__refresh_token_expiry = tokens["refreshTokenExpiry"]
        self.__refresh_token_ttl = tokens["refreshTokenTtl"]
        self.__user_id = tokens["userId"]
        self.__org_id = tokens["orgId"]

    async def __aenter__(self):
        self.__set_tokens(await self.__request_tokens(TokenRequestType.KEY))
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        pass

    async def refresh_access_token(self):
        self.__set_tokens(
            await self.__request_tokens(TokenRequestType.SESSION)
        )
