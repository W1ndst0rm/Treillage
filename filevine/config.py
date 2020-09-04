import filevine
import yaml


def get_credentials(credentials_file):
    with open(credentials_file) as f:
        credentials = yaml.safe_load(f)
    return filevine.ModelFactory(credentials)
