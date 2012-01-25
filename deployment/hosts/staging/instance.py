from fabric.api import env, settings, hide, abort
from fabric.colors import *
from fabric.contrib.files import exists, append
import os
import datetime

import deployment.utils as utils


class StagingInstance(object):
    """
    Instance for this project on StagingHost
    ========================================

    Example instance structure on staging server:

        /var/www/vhosts/s-PROJECTNAME/07aeb1319f4fbb2458028035c4c25a3044015be6/
            backup/
            env/
            media/          =>  /var/www/vhosts/s-PROJECTNAME/media
            PROJECTNAME/
    """

    stamp = None

    def __init__(self, *args, **kwargs):
        """ Set instance stamp to HEAD by default. """

        self.stamp = utils.source.get_head()

    def create_stamp(self, branch, commit):
        """ Create identifier for instance based on git IDs """

        if not commit is None:
            return commit

        if not branch is None:
            return utils.source.get_commit_id(branch)

        return utils.source.get_head()

    def check_deploy(self):
        """ Check deployment requirements and aborts task if not ok. """

        current_instance_stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        previous_instance_stamp = utils.instance.get_instance_stamp(env.previous_instance_path)

        if self.stamp == current_instance_stamp:
            abort(red('Deploy aborted because %s is already the current instance.' % self.stamp))

        if self.stamp == previous_instance_stamp:
            abort(red('Deploy aborted because %s is the previous instance. Use rollback task instead.' % self.stamp))

        if exists(env.instance_path):
            # TODO: ask for overwrite?
            abort(red('Deploy aborted because instance %s has already been deployed.' % self.stamp))

    def create_folders(self):

        print(green('\nCreating folders.'))
        folders_to_create = [
            env.instance_path,
            env.backup_path,
            env.source_path,
            env.virtualenv_path,
        ]

        for folder in folders_to_create:
            utils.commands.create_folder(folder) 

    def deploy_source(self):
        """ Deploy by branch of commit_id (defaults to master/HEAD) """

        print(green('\nDeploying source for %s.' % self.stamp))
        utils.source.transfer_source(upload_path=env.source_path, tree=self.stamp)

    def copy_settings_file(self):
        """ Copy django settings from project to instance """

        print(green('\nCopying settings.'))
        utils.commands.copy(
            from_path = os.path.join(env.project_path, 'settings.py'),
            to_path = os.path.join(env.source_path, 'settings.py')
        )

    def link_media_folder(self):
        """ Link instance media folder to project media folder """

        print(green('\nLinking media folder.'))
        utils.commands.create_symbolic_link(
            real_path = os.path.join(env.project_path, 'media'),
            symbolic_path = os.path.join(env.instance_path, 'media')
        )

    def collect_static_files(self):

        print(green('\nCollecting static files.'))
        command = 'collectstatic --link --noinput --verbosity=0 --traceback'
        utils.commands.django_manage(env.virtualenv_path, env.source_path, command)

    def create_virtualenv(self):

        print(green('\nCreating virtual environment.'))
        utils.instance.create_virtualenv(env.virtualenv_path, env.user)

        print(green('\nPip installing requirements.'))
        utils.instance.pip_install_requirements(
            env.virtualenv_path,
            env.source_path,
            env.cache_path,
            env.log_path
        )

    def delete(self):
        """ Delete instance from filesystem """

        print(green('\nRemoving instance from filesystem for %s.' % self.stamp))
        utils.commands.delete_folder(env.instance_path)

    def update_database(self, migrate=False, backup=True):

        if backup:
            print(green('\nBacking up database at start.'))
            self.backup_database(postfix='_start')

        print(green('\nSyncing database.'))
        utils.commands.django_manage(env.virtualenv_path, env.source_path, 'syncdb')

        if migrate:
            print(green('\nMigrating database.'))
            utils.commands.django_manage(env.virtualenv_path, env.source_path, 'migrate')

        if backup:
            print(green('\nBacking up database at end.'))
            self.backup_database(postfix='_end')

    def backup_database(self, postfix=''):

        backup_file = os.path.join(env.backup_path, 'db_backup%s.sql' % postfix)
        python_command = '%s/db_backup.py "%s"' % (env.scripts_path, backup_file)
        utils.commands.python_run(env.virtualenv_path, python_command)

    def restore_database(self):

        backup_file = os.path.join(env.backup_path, 'db_backup_start.sql')

        utils.commands.python_run(env.virtualenv_path, '%s/db_drop.py' % env.scripts_path)
        utils.commands.python_run(env.virtualenv_path, '%s/db_create.py' % env.scripts_path)
        utils.commands.sql_execute_file(env.virtualenv_path, env.scripts_path, backup_file)

    def set_current(self):

        print(green('\nUpdating instance symlinks.'))
        utils.instance.set_current_instance(env.project_path, env.instance_path)

    def check_rollback(self):
        """ Check requirements for rollback and abort if not ok. """

        backup_file = os.path.join(env.backup_path, 'db_backup_start.sql')

        if not exists(env.previous_instance_path):
            abort(red('No rollback possible. No previous instance found to rollback to.'))

        if not exists(backup_file):
            abort(red('Could not find backupfile to restore database with.'))

    def rollback(self):
        """ Removes current instance and rolls back to previous (if any). """

        print(green('\nRestoring database to start of this instance.'))
        self.restore_database()

        print(green('\nRemoving this instance and set previous to current.'))
        utils.instance.rollback(env.project_path)

    def log(self, task_name, success=True):

        if success:
            result = 'SUCCESS'
        else:
            result = 'FAILED'

        message = '[%s] %s %s in STAGING by %s for %s' % (
            datetime.datetime.today().strftime('%Y-%m-%d %H:%M'),
            task_name.upper(),
            result,
            env.local_user.upper(),
            self.stamp
        )

        append(os.path.join(env.log_path, 'fabric.log'), message)