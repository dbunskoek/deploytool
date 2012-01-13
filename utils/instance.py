import datetime
from fabric.api import *
from fabric.contrib.files import *

import utils


def create_stamp():
    """ Creates datetime stamp for git tags and sqldumps (e.g. 1110191605) """

    instance = datetime.datetime.today().strftime('%y%m%d%H%M')

    if int(instance) in utils.source.list_tags():
        abort(red('Datetime-stamp already exist. Task aborted.'))

    return instance


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


def create_virtualenv(virtualenv_path, source_path, cache_path, log_path):
    """ Creates virtual environment for instance and installs packages. """

    requirements_file = os.path.join(source_path, 'requirements.txt')

    with settings(hide('stdout'), warn_only=True):
        run('virtualenv %s --no-site-packages' % virtualenv_path)

    if not exists(requirements_file) or not exists(virtualenv_path):
        abort(red('Could not install packages. Virtual environment or requirements.txt not found.'))

    with settings(hide('stdout'), warn_only=True):
        pip_log_file = os.path.join(log_path, 'pip.log')
        run('rm -f %s' % pip_log_file)
        run('pip install -E %s -r %s --download-cache=%s --log=%s' % (
                virtualenv_path,
                requirements_file,
                cache_path,
                pip_log_file
            )
        )


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
