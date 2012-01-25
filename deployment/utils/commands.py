from fabric.api import run
import os
import subprocess


def create_folder(path):

    if exists(path):
        abort(red('Path `%s` already exists.' % path))
    else:
        run('mkdir %s' % path)


def delete_folder(path):

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
    """ Helper to execute Python commands for current virtual environment """

    return run('%s/bin/python %s' % (virtualenv_path, command))


def django_manage(virtualenv_path, source_path, command):
    """ Helper to execute Django management commands """

    python_path = os.path.join(source_path, 'manage.py')
    python_command = '%s %s' % (python_path, command)
    python_run(virtualenv_path, python_command)


def sql_execute_query(virtualenv_path, scripts_path, query):
    """ Helper to execute mysql command executing supplied query """

    python_command = '%s/sql_query.py "%s"' % (scripts_path, query)
    python_run(virtualenv_path, python_command)


def sql_execute_file(virtualenv_path, scripts_path, filename):
    """ Helper to execute mysql file """

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
