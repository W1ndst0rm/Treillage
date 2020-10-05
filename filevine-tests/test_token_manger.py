import unittest
import asyncio
from filevine import get_credentials, TokenManager, BaseURL


class TestTokenManager(unittest.TestCase):
    def test_async_context_manager(self):
        async def test():
            base_url = 'http://127.0.0.1:4010'
            # base_url = BaseURL.UNITED_STATES.value
            credentials = get_credentials('../credentials/creds.yml')
            async with TokenManager(credentials, base_url) as tm:
                self.assertTrue(tm.access_token is not None)
                self.assertTrue(tm.access_token_expiry is not None)
                self.assertTrue(tm.refresh_token is not None)
        asyncio.run(test())

    def test_async_create(self):
        async def test():
            base_url = 'http://127.0.0.1:4010'
            # base_url = BaseURL.UNITED_STATES.value
            credentials = get_credentials('../credentials/creds.yml')
            tm = await TokenManager.create(credentials, base_url)
            self.assertTrue(tm.access_token is not None)
            self.assertTrue(tm.access_token_expiry is not None)
            self.assertTrue(tm.refresh_token is not None)
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
                self.assertTrue(old_access_token != tm.access_token)
                self.assertTrue(old_refresh_token != tm.refresh_token)
                self.assertTrue(old_access_token_expiry < tm.access_token_expiry)
        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
