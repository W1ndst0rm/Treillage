import aiohttp
import asyncio
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch
from treillage import (ConnectionManager, RateLimiter, TokenManager,
                       Credential, TreillageHTTPException,
                       TreillageRateLimitException)


class MockTokenManager(TokenManager):
    def __init__(self, credentials, base_url):
        super().__init__(credentials, base_url)
        self.__access_token = 'mock_access_token'
        self.__refresh_token = 'mock_refresh_token'
        self.__access_token_expiry = int(
            (datetime.now() + timedelta(seconds=5)).timestamp()
        )

    @classmethod
    async def create(cls, credentials, base_url):
        self = MockTokenManager(credentials, base_url)
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

    async def refresh_access_token(self):
        await asyncio.sleep(1)
        self.__access_token_expiry = int(
            (datetime.now() + timedelta(seconds=5)).timestamp()
        )


class MockResponse:
    def __init__(self, status):
        self.status = status
        self.data = {'items': []}
        self.url = 'http://127.0.0.1'

    async def json(self):
        return self.data

    async def text(self):
        return None


class TestConnectionManager(unittest.TestCase):
    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    def test_create(self):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            self.assertIsNone(conn.connector)
            self.assertIsNone(conn.rate_limiter)
            self.assertIsInstance(conn.token_manager, TokenManager)
            await conn.close()

            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret=''),
                max_connections=20
            )
            self.assertIsInstance(conn.connector, aiohttp.TCPConnector)
            self.assertIsNone(conn.rate_limiter)
            self.assertIsInstance(conn.token_manager, TokenManager)
            await conn.close()

            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret=''),
                rate_limit_token_regen_rate=10
            )
            self.assertIsInstance(conn.rate_limiter, RateLimiter)
            self.assertIsInstance(conn.token_manager, TokenManager)
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    def test_setup_headers(self):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            headers = conn._ConnectionManager__setup_headers({
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            })
            self.assertEqual(
                headers["x-fv-sessionid"],
                conn.token_manager.refresh_token
            )
            self.assertEqual(
                headers["Authorization"],
                f"Bearer {conn.token_manager.access_token}"
            )
            self.assertEqual(
                headers["Accept-Encoding"],
                "gzip, deflate, br"
            )
            self.assertEqual(
                headers["Connection"],
                "keep-alive"
            )
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    def test_handle_response(self):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            response = MockResponse(200)
            self.assertEqual(
                await conn._ConnectionManager__handle_response(response, 200),
                response.data
            )

            # test 500 server error
            with self.assertRaises(TreillageHTTPException):
                response = MockResponse(500)
                await conn._ConnectionManager__handle_response(response, 200)
            # test 429 Rate Limit error
            with self.assertRaises(TreillageRateLimitException):
                response = MockResponse(429)
                await conn._ConnectionManager__handle_response(response, 200)
            # test unexpected 2xx success code
            with self.assertRaises(TreillageHTTPException):
                response = MockResponse(200)
                await conn._ConnectionManager__handle_response(response, 204)

            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('treillage.connection_manager.RateLimiter', autospec=True)
    def test_handle_response_rate_limiter_fail(self, mock_rate_limiter):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                rate_limit_token_regen_rate=10,
                credentials=Credential(key='', secret='')
            )
            # test 429 Rate Limit error
            with self.assertRaises(TreillageRateLimitException):
                response = MockResponse(429)
                await conn._ConnectionManager__handle_response(response, 200)
            mock_rate_limiter.return_value.\
                last_try_success.assert_called_with(False)
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('treillage.connection_manager.RateLimiter', autospec=True)
    def test_handle_response_rate_limiter_success(self, mock_rate_limiter):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                rate_limit_token_regen_rate=10,
                credentials=Credential(key='', secret='')
            )
            response = MockResponse(204)
            self.assertEqual(
                await conn._ConnectionManager__handle_response(response, 204),
                response.data
            )
            mock_rate_limiter.return_value.\
                last_try_success.assert_called_with(True)
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('treillage.connection_manager.RateLimiter', autospec=True)
    def test_handle_response_error_with_rate_limiter(self, mock_rate_limiter):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                rate_limit_token_regen_rate=10,
                credentials=Credential(key='', secret='')
            )
            response = MockResponse(200)
            with self.assertRaises(TreillageHTTPException):
                await conn._ConnectionManager__handle_response(response, 500)
            self.assertFalse(
                mock_rate_limiter.return_value.last_try_success.called
            )
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('aiohttp.ClientSession', autospec=True)
    def test_get_request(self, mock_session):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            try:
                await conn.get(endpoint='/')
            except TreillageHTTPException:
                pass
            mock_session.return_value.get.assert_called_with(
                url='http://127.0.0.1:4010/',
                params=None,
                headers={
                    'x-fv-sessionid': 'mock_refresh_token',
                    'Authorization': 'Bearer mock_access_token'
                }
            )
            try:
                await conn.get(
                    endpoint='/test2',
                    params={'firstName': 'Joe'},
                    headers={"Accept-Encoding": "gzip, deflate, br"})
            except TreillageHTTPException:
                pass
            mock_session.return_value.get.assert_called_with(
                url='http://127.0.0.1:4010/test2',
                params={'firstName': 'Joe'},
                headers={
                    'Accept-Encoding': 'gzip, deflate, br',
                    'x-fv-sessionid': 'mock_refresh_token',
                    'Authorization': 'Bearer mock_access_token'
                }
            )
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('aiohttp.ClientSession', autospec=True)
    def test_patch_request(self, mock_session):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            try:
                await conn.patch(
                    endpoint='/patch',
                    body={'firstName': 'John', 'lastName': 'Doe'}
                )
            except TreillageHTTPException:
                pass
            mock_session.return_value.patch.assert_called_with(
                url='http://127.0.0.1:4010/patch',
                body={'firstName': 'John', 'lastName': 'Doe'},
                headers={
                    'x-fv-sessionid': 'mock_refresh_token',
                    'Authorization': 'Bearer mock_access_token'
                }
            )
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('aiohttp.ClientSession', autospec=True)
    def test_post_request(self, mock_session):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret=''))
            try:
                await conn.post(
                    endpoint='/post',
                    body={'firstName': 'John', 'lastName': 'Doe'}
                )
            except TreillageHTTPException:
                pass
            mock_session.return_value.post.assert_called_with(
                url='http://127.0.0.1:4010/post',
                body={'firstName': 'John', 'lastName': 'Doe'},
                headers={
                    'x-fv-sessionid': 'mock_refresh_token',
                    'Authorization': 'Bearer mock_access_token'
                }
            )
            await conn.close()
        asyncio.run(test())

    @patch('treillage.connection_manager.TokenManager', MockTokenManager)
    @patch('aiohttp.ClientSession', autospec=True)
    def test_delete_request(self, mock_session):
        async def test():
            conn = await ConnectionManager.create(
                base_url='http://127.0.0.1:4010',
                credentials=Credential(key='', secret='')
            )
            try:
                await conn.delete(endpoint='/delete')
            except TreillageHTTPException:
                pass
            mock_session.return_value.delete.assert_called_with(
                url='http://127.0.0.1:4010/delete',
                headers={
                    'x-fv-sessionid': 'mock_refresh_token',
                    'Authorization': 'Bearer mock_access_token'
                }
            )
            await conn.close()
        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
