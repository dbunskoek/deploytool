import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *


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

    return run('readlink -f %s' % instance_path).strip()[-40:]


def set_current_instance(project_path, instance_path):
    """ Delete previous, set current to previous and new to current """

    with cd(project_path):
        delete_folder('./previous_instance')

        if exists('./current_instance'):
            rename('./current_instance', './previous_instance')

        create_symbolic_link(instance_path, './current_instance')


def rollback(project_path):
    """ Remove current instance and rename previous to current """

    with cd(project_path):
        if exists('./previous_instance'):
            delete_folder('./current_instance')
            rename('./previous_instance', './current_instance')
