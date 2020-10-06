import unittest
import asyncio
from treillage import get_credentials, TokenManager, BaseURL


class TestTokenManager(unittest.TestCase):
    def test_async_context_manager(self):
        async def test():
            base_url = 'http://127.0.0.1:4010'
            # base_url = BaseURL.UNITED_STATES.value
            credentials = get_credentials('../credentials/creds.yml')
            async with TokenManager(credentials, base_url) as tm:
                self.assertIsNotNone(tm.access_token)
                self.assertIsNotNone(tm.access_token_expiry)
                self.assertIsNotNone(tm.refresh_token)
        asyncio.run(test())

    def test_async_create(self):
        async def test():
            base_url = 'http://127.0.0.1:4010'
            # base_url = BaseURL.UNITED_STATES.value
            credentials = get_credentials('../credentials/creds.yml')
            tm = await TokenManager.create(credentials, base_url)
            self.assertIsNotNone(tm.access_token)
            self.assertIsNotNone(tm.access_token_expiry)
            self.assertIsNotNone(tm.refresh_token)
        asyncio.run(test())

    def test_refresh_access_token(self):
        async def test():
            # base_url = 'http://127.0.0.1:4010'
            base_url = BaseURL.UNITED_STATES.value
            credentials = get_credentials('../credentials/creds.yml')
            async with TokenManager(credentials, base_url) as tm:
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
