from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
import os
import subprocess


def create_tarball(project_path, target, file_name='archive.tar'):
    """ Create archive from target file/folder """

    with cd(project_path):
        run('tar -cf ./%s ./%s' % (file_name, target))


def download_file(remote_path, local_path, delete_remote=True):

    get(remote_path, local_path)

    if delete_remote:
        delete(remote_path)


def tail_file(file_path, lines=5):
    """ Output the last lines from a file to console """

    return run('tail --lines=5 %s' % file_path)


def read_link(path):
    """ Returns real path for symbolic link """

    return run('readlink -f %s' % path).strip()


def create_folder(path):

    if exists(path):
        abort(red('Path `%s` already exists.' % path))
    else:
        run('mkdir %s' % path)


def delete(path):

    run('rm -rf %s' % path)


def create_symbolic_link(real_path, symbolic_path):

    run('ln -sf %s %s' % (real_path, symbolic_path))


def copy(from_path, to_path):

    run('cp %s %s' % (from_path, to_path))


def rename(old_path, new_path):

    run('mv %s %s' % (old_path, new_path))


def touch_wsgi(project_path):
    """ Touch WSGI to restart website """

    return run('touch %s/django.wsgi' % project_path)


def python_run(virtualenv_path, command):
    """ Execute Python commands for current virtual environment """

    return run('%s/bin/python %s' % (virtualenv_path, command))


def django_manage(virtualenv_path, source_path, command):
    """ Execute Django management command """

    python_path = os.path.join(source_path, 'manage.py')
    python_command = '%s %s' % (python_path, command)
    python_run(virtualenv_path, python_command)


def sql_execute_query(virtualenv_path, scripts_path, query):
    """ Execute mysql command for supplied query """

    python_command = '%s/sql_query.py "%s"' % (scripts_path, query)
    python_run(virtualenv_path, python_command)


def sql_execute_file(virtualenv_path, scripts_path, filename):
    """ Execute mysql file """

    python_command = '%s/sql_file.py "%s"' % (scripts_path, filename)
    python_run(virtualenv_path, python_command)


def subprocess_popen(args):
    """
    Helper to execute a command in a subprocess
        - output and errors are piped to a string
        - raw output-string is returned

    See also
        - http://docs.python.org/library/subprocess.html
        - http://stackoverflow.com/questions/3947191/getting-the-entire-output-from-subprocess-popen/3947224#3947224
    """

    if args:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return proc.communicate()[0]
    else:
        return ''
