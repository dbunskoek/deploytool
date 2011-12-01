import os

import utils


class StagingInstance(object):
    """ Helpers for creating a project-instance on staging-environment """

    def __init__(self, *args, **kwargs):

        self.stamp = utils.instance.create_stamp()

    def create(self, env):
        """ Creates project-instance from fabric-environment """

        self.create_folders(env)
        self.deploy_source(env.project_vcs_wget, env.source_path)
        self.create_virtualenv(env.virtualenv_path, env.source_path, env.cache_path)
        self.copy_settings_file(env.project_path, env.source_path)
        self.link_media_folder(env.project_path, env.instance_path)
        self.collect_static_files()

    def create_folders(self, env):

        folders = [
            env.instance_path,
            env.backup_path,
            env.source_path,
            env.virtualenv_path,
        ]

        for folder in folders:
            utils.instance.create_folder(folder) 
            
    def deploy_source(self, download_url, upload_path):
        """ Tag VCS, and transfer source from VCS to staging """

        utils.source.create_tag(self.stamp)
        utils.source.transfer_source(
            download_url = download_url,
            upload_path = upload_path,
            tag = self.stamp
        )

    def copy_settings_file(self, project_path, source_path):
        """ Copy django settings from project to instance """

        utils.instance.copy(
            from_path = os.path.join(project_path, 'settings.py'),
            to_path = os.path.join(source_path, 'settings.py')
        )

    def link_media_folder(self, project_path, instance_path):
        """ Link instance media folder to project media folder """

        utils.instance.create_symbolic_link(
            real_path = os.path.join(project_path, 'media'),
            symbolic_path = os.path.join(instance_path, 'media')
        )

    def collect_static_files(self):

        utils.commands.django_manage('collectstatic --link --noinput')

    def create_virtualenv(self, virtualenv_path, source_path, cache_path):

        utils.instance.create_virtualenv(
            virtualenv_path = virtualenv_path,
            source_path = source_path,
            cache_path = cache_path
        )

    def delete(self, env):
        """ Delete instance from filesystem and remove tag from VCS """

        utils.instance.delete_folder(env.instance_path)
        utils.source.delete_tag(self.stamp)

    def update_database(self, env, migrate=False, backup=True):

        if backup:
            self.backup_database(env, postfix='_start')

        utils.commands.django_manage('syncdb')

        if migrate:
            utils.commands.django_manage('migrate')

        if backup:
            self.backup_database(env, postfix='_end')

    def backup_database(self, env, postfix=''):

        backup_file = os.path.join(env.backup_path, 'db_backup%s.sql' % postfix)
        utils.commands.python_run('%s/db_backup.py "%s"' % (env.scripts_path, backup_file))

    def restore_database(self, env):

        backup_file = os.path.join(env.backup_path, 'db_backup_start.sql')

        utils.commands.python_run('%s/db_drop.py' % env.scripts_path)
        utils.commands.python_run('%s/db_create.py' % env.scripts_path)
        utils.commands.sql_execute_file(backup_file)

    def update_webserver(self, env):

        utils.instance.set_current(env.project_path, env.instance_path)
        utils.commands.touch_wsgi(env.project_path)

