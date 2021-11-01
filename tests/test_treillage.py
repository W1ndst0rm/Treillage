import asyncio
import unittest
from unittest.mock import patch
from treillage import Treillage, BaseURL


@patch('treillage.treillage.Credential', autospec=True)
@patch('treillage.treillage.ConnectionManager', autospec=True)
class TestTreillage(unittest.TestCase):
    def test_context_manager(self, mock_connection_manager, mock_credential):
        async def test():
            async with Treillage(
                    credentials_file='creds.yml',
                    base_url=BaseURL.UNITED_STATES
            ) as tr:
                self.assertIsNotNone(tr.conn)
                mock_credential.get_credentials.assert_called_once_with(
                    'creds.yml'
                )
                mock_connection_manager.create.assert_called_once_with(
                    BaseURL.UNITED_STATES.value,
                    tr._Treillage__credential,
                    None,
                    None
                )

        asyncio.run(test())

    def test_create(self, mock_connection_manager, mock_credential):
        async def test():
            tr = await Treillage.create(
                credentials_file='creds.yml',
                base_url=BaseURL.UNITED_STATES,
                max_connections=10,
                rate_limit_token_regen_rate=30
            )
            self.assertIsNotNone(tr.conn)
            mock_credential.get_credentials.assert_called_once_with(
                'creds.yml'
            )
            mock_connection_manager.create.assert_called_once_with(
                BaseURL.UNITED_STATES.value,
                tr._Treillage__credential,
                10,
                30
            )
            await tr.close()

        asyncio.run(test())

    def test_context_manager_url_as_string(self,
                                           mock_connection_manager,
                                           mock_credential):
        async def test():
            async with Treillage(
                    credentials_file='creds.yml',
                    base_url="https://api.filevine.io"
            ) as tr:
                self.assertIsNotNone(tr.conn)
                mock_credential.get_credentials.assert_called_once_with(
                    'creds.yml'
                )
                mock_connection_manager.create.assert_called_once_with(
                    "https://api.filevine.io",
                    tr._Treillage__credential,
                    None,
                    None
                )

        asyncio.run(test())

    def test_context_manager_with_max_connections(self,
                                                  mock_connection_manager,
                                                  mock_credential):
        async def test():
            async with Treillage(
                    credentials_file='creds.yml',
                    base_url=BaseURL.UNITED_STATES,
                    max_connections=10
            ) as tr:
                self.assertIsNotNone(tr.conn)
                mock_credential.get_credentials.assert_called_once_with(
                    'creds.yml'
                )
                mock_connection_manager.create.assert_called_once_with(
                    BaseURL.UNITED_STATES.value,
                    tr._Treillage__credential,
                    10,
                    None
                )

        asyncio.run(test())

    def test_context_manager_with_rate_limiter(self,
                                               mock_connection_manager,
                                               mock_credential):
        async def test():
            async with Treillage(
                    credentials_file='creds.yml',
                    base_url=BaseURL.UNITED_STATES,
                    rate_limit_token_regen_rate=20
            ) as tr:
                self.assertIsNotNone(tr.conn)
                mock_credential.get_credentials.assert_called_once_with(
                    'creds.yml'
                )
                mock_connection_manager.create.assert_called_once_with(
                    BaseURL.UNITED_STATES.value,
                    tr._Treillage__credential,
                    None,
                    20
                )

        asyncio.run(test())

    def test_context_manager_with_all_options(self,
                                              mock_connection_manager,
                                              mock_credential):
        async def test():
            async with Treillage(
                    credentials_file='creds.yml',
                    base_url=BaseURL.UNITED_STATES,
                    max_connections=10,
                    rate_limit_token_regen_rate=20
            ) as tr:
                self.assertIsNotNone(tr.conn)
                mock_credential.get_credentials.assert_called_once_with(
                    'creds.yml'
                )
                mock_connection_manager.create.assert_called_once_with(
                    BaseURL.UNITED_STATES.value,
                    tr._Treillage__credential,
                    10,
                    20
                )

        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
