import jwt
import time
import unittest
from unittest.mock import patch
from secrets import token_urlsafe
import asyncio
from treillage import ModelFactory, TokenManager


async def mock_json():
    key = 'some secret for testing'
    now = int(time.time())
    access_payload = {
        "userId": "12345",
        "orgId": "4321",
        "keyId": "fvpk_00000000-0000-0000-0000-000000000000",
        "scopes": "core:api",
        "iat": now,
        "exp": now + 900,
        "aud": "filevine.io",
        "iss": "filevine.io",
        "sub": "12345"
    }
    body = dict()
    body['accessToken'] = jwt.encode(access_payload, key, algorithm='HS256')
    body['refreshToken'] = jwt.encode({}, token_urlsafe(), algorithm='HS256')
    body['refreshTokenExpiry'] = now + 86400
    body['refreshTokenTtl'] = '24 hours'
    body['userId'] = '12345'
    body['orgId'] = 6355
    return body


class TestTokenManager(unittest.TestCase):
    def setUp(self) -> None:
        self.base_url = 'http://127.0.0.1'
        self.credentials = ModelFactory({'key': '', 'secret': ''})
        patcher = patch('treillage.token_manager.ClientSession.post')
        mock_post = patcher.start()
        mock_response = mock_post.return_value.__aenter__.return_value
        mock_response.json.side_effect = mock_json
        mock_response.status = 200
        self.addCleanup(patcher.stop)

    def test_async_context_manager(self):
        async def test():
            async with TokenManager(self.credentials, self.base_url) as tm:
                self.assertIsNotNone(tm.access_token)
                self.assertIsNotNone(tm.access_token_expiry)
                self.assertIsNotNone(tm.refresh_token)
        asyncio.run(test())

    def test_async_create(self):
        async def test():
            tm = await TokenManager.create(self.credentials, self.base_url)
            self.assertIsNotNone(tm.access_token)
            self.assertIsNotNone(tm.access_token_expiry)
            self.assertIsNotNone(tm.refresh_token)
        asyncio.run(test())

    def test_refresh_access_token(self):
        async def test():
            async with TokenManager(self.credentials, self.base_url) as tm:
                old_access_token = tm.access_token
                old_access_token_expiry = tm.access_token_expiry
                old_refresh_token = tm.refresh_token
                await asyncio.sleep(5)
                await tm.refresh_access_token()
                self.assertNotEqual(old_access_token, tm.access_token)
                self.assertNotEqual(old_refresh_token, tm.refresh_token)
                self.assertLess(
                    old_access_token_expiry, tm.access_token_expiry
                )
        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
