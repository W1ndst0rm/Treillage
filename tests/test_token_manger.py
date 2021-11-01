import jwt
import time
import unittest
from unittest.mock import patch
from secrets import token_urlsafe
import asyncio
from treillage import Credential, TokenManager


async def mock_json():
    # This key exists only here for testing.
    key = b"""-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""
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
    body['accessToken'] = jwt.encode(access_payload, key=key, algorithm='RS256')
    body['refreshToken'] = jwt.encode({"key": token_urlsafe()}, key=key, algorithm='RS256')
    body['refreshTokenExpiry'] = now + 86400
    body['refreshTokenTtl'] = '24 hours'
    body['userId'] = '12345'
    body['orgId'] = 6355
    return body


class TestTokenManager(unittest.TestCase):
    def setUp(self) -> None:
        self.base_url = 'http://127.0.0.1'
        self.credentials = Credential(key='', secret='')
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
