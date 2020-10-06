import unittest
import os
from treillage import get_credentials, TreillageException


class TestCredentialImport(unittest.TestCase):
    @staticmethod
    def get_credentials(test_cred_data):
        creds_file = 'creds.yml'
        with open(creds_file, 'w') as out:
            for k in test_cred_data:
                out.write(f"{k}: {test_cred_data[k]}\n")
        try:
            credentials = get_credentials(creds_file)
            return credentials
        finally:
            os.remove(creds_file)

    def test_success(self):
        creds_data = {
            'key': 'fvpk_00000000-0000-0000-0000-000000000000',
            'secret': 'fvsk_0000000000000000000000000000000000000000000000000',
            'queueid': 'q12345678901'

        }
        credentials = self.get_credentials(creds_data)
        self.assertEqual(credentials.key, creds_data['key'])
        self.assertEqual(credentials.secret, creds_data['secret'])
        self.assertEqual(credentials.queueid, creds_data['queueid'])

    def test_missing_key(self):
        creds_data = {
            'secret': 'fvsk_0000000000000000000000000000000000000000000000000',
            'queueid': 'q12345678901'

        }
        with self.assertRaises(TreillageException):
            self.get_credentials(creds_data)

    def test_missing_secret(self):
        creds_data = {
            'key': 'fvpk_00000000-0000-0000-0000-000000000000',
            'queueid': 'q12345678901'

        }
        with self.assertRaises(TreillageException):
            self.get_credentials(creds_data)


if __name__ == '__main__':
    unittest.main()
