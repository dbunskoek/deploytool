from fabric.api import *
import os
import subprocess


def touch_wsgi(project_path):
    """ Touch WSGI to restart website """

    return run('touch %s/django.wsgi' % project_path)


def python_run(command):
    """ Helper to execute Python commands for current virtual environment """

    return run('%s/bin/python %s' % (env.virtualenv_path, command))


def django_manage(command):
    """ Helper to execute Django management commands """

    with settings(hide('stdout'), warn_only=True):
        path = os.path.join(env.source_path, 'manage.py')
        python_run('%s %s' % (path, command))


def sql_execute_query(query):
    """ Helper to execute mysql command executing supplied query """

    path = os.path.join(env.project_path, env.scripts_path)
    python_run('%s/sql_query.py "%s"' % (path, query))


def sql_execute_file(filename):
    """ Helper to execute mysql file """

    path = os.path.join(env.project_path, env.scripts_path)
    python_run('%s/sql_file.py "%s"' % (path, filename))


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
