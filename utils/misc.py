from fabric import *
from fabric.api import env
from pprint import pprint


def print_env():
    """ PrettyPrints fabric environment to stdout """

    pprint(env, indent=4)


def get_remote_file(remote_file_path, local_file_path, delete_remote_file=False):
    """ Download a file from remote server to local machine """

    get(remote_file_path, local_file_path)

    if delete_remote_file:
        run('rm -rf %s' % remote_file_path)


def write_log(message, log_path, log_file='fabric.log'):
    """ Logs message """

    raise NotImplementedError
