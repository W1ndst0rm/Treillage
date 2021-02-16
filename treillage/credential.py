from .exceptions import TreillageException
import yaml


class Credential:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    @classmethod
    def get_credentials(cls, credentials_file):
        with open(credentials_file) as file:
            credentials_data = yaml.safe_load(file)
        if 'key' not in credentials_data or 'secret' not in credentials_data:
            raise TreillageException(
                msg=("Credentials file must contain 'key' and 'secret'"
                     "as top level key-value pairs"))
        else:
            return Credential(
                credentials_data['key'],
                credentials_data['secret']
            )
