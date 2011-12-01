from fabric import *
from pprint import pprint


def print_env():
    """ PrettyPrints fabric environment to stdout """

    pprint(env, indent=4)


def get_remote_file(remote_file_path, local_file_path, delete_remote_file=False):
    """ Download a file from remote server to local machine """

    get(remote_file_path, local_file_path)

    if delete_remote_file:
        run('rm -rf %s' % remote_file_path)


def write_log(task, instance='', log_file='fabric.log'):
    """ Logs executed task """

    if instance:
        instance = ' for %s' % instance

    fabric_log_file = os.path.join(env.log_path, log_file)
    msg = '[%s]\t%s in %s by %s%s' % (
        datetime.datetime.today().strftime('%Y-%m-%d %H:%M'),
        task.upper(),
        env.environment.upper(),
        env.local_user.upper(),
        instance
    )
    append(fabric_log_file, msg)
