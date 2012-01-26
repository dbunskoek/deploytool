import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *

import commands


def create_virtualenv(virtualenv_path, project_user):
    """ Creates virtual environment for instance and installs packages. """

    run('virtualenv %s --no-site-packages' % virtualenv_path)


def pip_install_requirements(virtualenv_path, source_path, cache_path, log_path):
    """ Requires availability of Pip (0.8.1 or later) on remote system """

    requirements_file = os.path.join(source_path, 'requirements.txt')
    log_file = os.path.join(log_path, 'pip.log')

    if not exists(requirements_file) or not exists(virtualenv_path):
        abort(red('Could not install packages. Virtual environment or requirements.txt not found.'))

    args = (virtualenv_path, requirements_file, cache_path, log_file)
    run('pip install -E %s -r %s --download-cache=%s --use-mirrors --quiet --log=%s' % args)


def get_instance_stamp(instance_path):
    """ Reads symlinked (current/previous) instance and returns its sliced off stamp (git commit SHA1)  """

    return commands.read_link(instance_path)[-40:]


def set_current_instance(project_path, instance_path):
    """ Delete previous, set current to previous and new to current """

    with cd(project_path):
        commands.delete('./previous_instance')

        if exists('./current_instance'):
            commands.rename('./current_instance', './previous_instance')

        commands.create_symbolic_link(instance_path, './current_instance')


def rollback(project_path):
    """ Remove current instance and rename previous to current """

    with cd(project_path):
        if exists('./previous_instance'):
            commands.delete('./current_instance')
            commands.rename('./previous_instance', './current_instance')
