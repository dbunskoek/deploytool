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

    run('ln -s %s %s' % (real_path, symbolic_path))


def copy(from_path, to_path):

    run('cp %s %s' % (from_path, to_path))


def create_virtualenv(virtualenv_path, project_user):
    """ SUDO - Creates virtual environment for instance and installs packages. """

    run('virtualenv %s --no-site-packages' % virtualenv_path)
    # sudo('chown -r %s:%s %s' % (project_user, project_user, virtualenv_path))


def pip_install_requirements(virtualenv_path, source_path, cache_path):
    """ Requires availability of Pip (0.8.1 or later) on remote system """

    requirements_file = os.path.join(source_path, 'requirements.txt')

    if not exists(requirements_file) or not exists(virtualenv_path):
        abort(red('Could not install packages. Virtual environment or requirements.txt not found.'))

    args = (virtualenv_path, requirements_file, cache_path)
    run('pip install -E %s -r %s --download-cache=%s --use-mirrors' % args)


def get_current_instance_stamp(current_instance_path):
    """ Reads symlinked current_instance and returns its sliced off stamp (git commit SHA1)  """

    return run('readlink -f %s' % current_instance_path).strip()[-40:]


def set_current(project_path, instance_path):
    """ Set current instance to previous and new to current """

    with cd(project_path):
        run('rm -rf ./previous_instance')

        if exists('./current_instance'):
            run('mv ./current_instance ./previous_instance')

        run('ln -sf %s ./current_instance' % instance_path)


def rollback(project_path):
    """ Remove current instance and rename previous to current """

    with cd(project_path):
        if exists('./previous_instance'):
            run('rm -rf ./current_instance')
            run('mv ./previous_instance ./current_instance')
