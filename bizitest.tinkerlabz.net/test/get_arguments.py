import yaml
import os
from yaml.loader import SafeLoader


def get_params(configFilename=r'configuration.yaml') -> object:
    with open(configFilename) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data


def get_filepath(filename):
    '''
    Provide the real path to the file to upload
    '''
    basedir = os.path.realpath('.')
    return os.path.join(basedir, filename)
