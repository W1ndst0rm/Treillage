from .models import ModelFactory
from .exceptions import FilevineException
import yaml


def get_credentials(credentials_file):
    with open(credentials_file) as f:
        credentials_data = yaml.safe_load(f)
    credentials = ModelFactory(credentials_data)
    if not hasattr(credentials, 'key') or not hasattr(credentials, 'secret'):
        raise FilevineException(msg="Credentials file must contain 'key' and 'secret' as top level key-value pairs")
    else:
        return credentials
