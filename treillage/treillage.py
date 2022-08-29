from .credential import Credential
from .connection_manager import ConnectionManager
from enum import Enum
from typing import Union


class BaseURL(Enum):
    UNITED_STATES = "https://api.filevine.io"
    CANADA = "https://api.filevine.ca"


class Treillage:
    def __init__(self,
                 credentials_file: str,
                 base_url: Union[str, BaseURL] = BaseURL.UNITED_STATES.value,
                 # Number of parallel connections to each host:port endpoint
                 max_connections: int = None,
                 # Maximum requests per second allowed by the rate-limiter
                 requests_per_second: int = None):
        self.__credential = Credential.get_credentials(credentials_file)
        if isinstance(base_url, BaseURL):
            self.__base_url = base_url.value
        elif isinstance(base_url, str):
            self.__base_url = base_url
        self.__max_connections = max_connections
        self.__requests_per_second = requests_per_second
        self.__conn = None

    @property
    def conn(self) -> ConnectionManager:
        return self.__conn

    async def __async_init(self):
        self.__conn = await ConnectionManager.create(
            self.__base_url,
            self.__credential,
            self.__max_connections,
            self.__requests_per_second
        )

    @classmethod
    async def create(
            cls,
            credentials_file: str,
            base_url: Union[str, BaseURL] = BaseURL.UNITED_STATES.value,
            max_connections: int = None,
            requests_per_second: int = None,
    ):
        self = Treillage(credentials_file,
                         base_url,
                         max_connections,
                         requests_per_second)
        await self.__async_init()
        return self

    async def close(self):
        await self.__conn.close()

    async def __aenter__(self):
        await self.__async_init()
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close()
