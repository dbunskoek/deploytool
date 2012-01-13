from fabric.api import env
from fabric.contrib.files import exists
import os

import utils


class StagingInstance(object):
    """ Helpers for creating a project-instance on staging-environment """

    def __init__(self, *args, **kwargs):
        """ Timestamp (i.e. 1201121500) is used for folder-name and VCS-tag """

        self.stamp = utils.instance.create_stamp()

    def deploy(self):
        """ Creates project-instance from fabric-environment """

        self.create_folders()
        self.deploy_source()
        self.create_virtualenv()
        self.copy_settings_file()
        self.link_media_folder()
        self.collect_static_files()

    def create_folders(self):

        folders_to_create = [
            env.instance_path,
            env.backup_path,
            env.source_path,
            env.virtualenv_path,
        ]

        for folder in folders_to_create:
            utils.instance.create_folder(folder) 

    def deploy_source(self):
        """ Tag VCS, and transfer source from VCS to staging """

        utils.source.create_tag(self.stamp)
        utils.source.transfer_source(
            download_url = env.project_vcs_wget,
            upload_path = env.source_path,
            tag = self.stamp
        )

    def copy_settings_file(self):
        """ Copy django settings from project to instance """

        utils.instance.copy(
            from_path = os.path.join(env.project_path, 'settings.py'),
            to_path = os.path.join(env.source_path, 'settings.py')
        )

    def link_media_folder(self):
        """ Link instance media folder to project media folder """

        utils.instance.create_symbolic_link(
            real_path = os.path.join(env.project_path, 'media'),
            symbolic_path = os.path.join(env.instance_path, 'media')
        )

    def collect_static_files(self):

        command = 'collectstatic --link --noinput --verbosity=0 --traceback'
        utils.commands.django_manage(env.virtualenv_path, env.source_path, command)

    def create_virtualenv(self):

        utils.instance.create_virtualenv(
            env.virtualenv_path,
            env.source_path,
            env.cache_path,
            env.log_path
        )

    def delete(self):
        """ Delete instance from filesystem and remove tag from VCS """

        utils.instance.delete_folder(env.instance_path)
        utils.source.delete_tag(self.stamp)

    def update_database(self, migrate=False, backup=True):

        if backup:
            self.backup_database(postfix='_start')

        utils.commands.django_manage(env.virtualenv_path, env.source_path, 'syncdb')

        if migrate:
            utils.commands.django_manage(env.virtualenv_path, env.source_path, 'migrate')

        if backup:
            self.backup_database(postfix='_end')

    def backup_database(self, postfix=''):

        backup_file = os.path.join(env.backup_path, 'db_backup%s.sql' % postfix)
        python_command = '%s/db_backup.py "%s"' % (env.scripts_path, backup_file)
        utils.commands.python_run(env.virtualenv_path, python_command)

    def restore_database(self):

        backup_file = os.path.join(env.backup_path, 'db_backup_start.sql')
        if not exists(backup_file):
            raise SystemExit('Could not find backupfile to restore database with.')

        utils.commands.python_run(env.virtualenv_path, '%s/db_drop.py' % env.scripts_path)
        utils.commands.python_run(env.virtualenv_path, '%s/db_create.py' % env.scripts_path)
        utils.commands.sql_execute_file(env.virtualenv_path, env.scripts_path, backup_file)

    def set_current(self):

        utils.instance.set_current(env.project_path, env.instance_path)

    def rollback(self):
        """ Removes current instance and rolls back to previous (if any). """

        # switch instances
        # update settings for changed current instance
        # restore database

        # utils.instance.rollback(env.project_path)
        # 
        # self.stamp = None
        # 
        # 
        # backup_file = os.path.join(env.current_instance_path, 'db_backup_start.sql')
        # self.restore_database(backup_file=backup_file)
