import datetime
from fabric.api import abort, env, settings, hide, local
from fabric.colors import *
from fabric.contrib.files import append, exists
from fabric.operations import require
from fabric.tasks import Task
import os

import deployment.utils as utils


class RemoteHost(Task):
    """ HOST: updates fabric environment """

    requirements = [
        'environment',
        'hosts',
        'project_name',
        'project_name_prefix',
        'projects_root',
    ]

    def __init__(self, *args, **kwargs):

        # use environment as task name
        self.name = kwargs['project_settings']['environment']

        # save project settings in instance
        self.settings = kwargs['project_settings']

    def run(self):

        # update fabric env with saved project settings (and check reqs.)
        env.update(self.settings)
        [require(r) for r in self.requirements]

        # update fabric env with host settings
        project_name = '%s%s' % (env.project_name_prefix, env.project_name)
        project_path = os.path.join(env.projects_root, project_name)
        env.update({
            'cache_path': os.path.join(project_path, 'cache'),
            'current_instance_path': os.path.join(project_path, 'current_instance'),
            'database_name': project_name,
            'environment': env.environment,
            'hosts': env.hosts,
            'log_path': os.path.join(project_path, 'log'),
            'media_path': os.path.join(project_path, 'media'),
            'previous_instance_path': os.path.join(project_path, 'previous_instance'),
            'project_root': env.projects_root,
            'project_path': project_path,
            'scripts_path': os.path.join(project_path, 'scripts'),
            'user': project_name,
        })


class RemoteTask(Task):
    """
    Base class for remote tasks
        - updates fabric env for instance
        - handles logging
    """

    requirements = [
        'project_path',
        'project_name',
    ]

    def __call__(self):
        """ Task implementation - called from self.run() """

        raise NotImplementedError

    def log(self, success):
        """ Single line task logging to ./log/fabric.log """

        if success == True:
            result = 'success'
        else:
            result = 'failed'

        message = '[%s] %s %s in %s by %s for %s' % (
            datetime.datetime.today().strftime('%Y-%m-%d %H:%M'),
            self.name,
            result,
            env.environment,
            env.local_user,
            self.stamp
        )

        append(os.path.join(env.log_path, 'fabric.log'), message)

    def run(self, *args, **kwargs):
        """ Hide output, update fabric env, run task """

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            self.update_fabric_environment()
            self()

    def update_fabric_environment(self):
        """ Check requirements and update fabric environment """

        # check for stamp which identifies a remote instance
        if self.stamp == None:
            abort(red('No stamp found for task.'))

        # check fabric env for required keys
        [require(r) for r in self.requirements]

        # update fabric env with instance settings
        instance_path = os.path.join(env.project_path, self.stamp)
        env.update({
            'backup_path': os.path.join(instance_path, 'backup'),
            'instance_stamp': self.stamp,
            'instance_path': instance_path,
            'source_path': os.path.join(instance_path, env.project_name),
            'virtualenv_path': os.path.join(instance_path, 'env'),
        })


class Deployment(RemoteTask):
    """
    TASK: Deploy new instance to staging

        Usage:

        # default deployment using current git HEAD
        $ fab staging.deploy

        # deployment for a specific git branch
        $ fab staging.deploy:branch=my-branch

        # deployment for a specific git commit ID
        $ fab staging.deploy:commit=1ec9d293ce54647df7f15ee7c0295b8eb2a5cbef
    """

    name = 'deploy'

    def run(self, *args, **kwargs):
        """ Load instance from CLI kwargs (commit/branch) or git HEAD """

        if kwargs.has_key('commit'):
            self.stamp = kwargs['commit']
        elif kwargs.has_key('branch'):
            self.stamp = utils.source.get_commit_id(kwargs['branch'])
        else:
            self.stamp = utils.source.get_head()

        super(Deployment, self).run(*args, **kwargs)

    def __call__(self):

        # check if deploy is possible
        if self.stamp == utils.instance.get_instance_stamp(env.current_instance_path):
            abort(red('Deploy aborted because %s is already the current instance.' % self.stamp))
        if self.stamp == utils.instance.get_instance_stamp(env.previous_instance_path):
            abort(red('Deploy aborted because %s is the previous instance. Use rollback task instead.' % self.stamp))
        if exists(env.instance_path):
            abort(red('Deploy aborted because instance %s has already been deployed.' % self.stamp))

        # start deploy
        try:
            print(green('\nCreating folders.'))
            folders_to_create = [
                env.instance_path,
                env.backup_path,
                env.source_path,
                env.virtualenv_path,
            ]
            for folder in folders_to_create:
                utils.commands.create_folder(folder) 

            print(green('\nDeploying source.'))
            utils.source.transfer_source(upload_path=env.source_path, tree=self.stamp)

            print(green('\nCreating virtual environment.'))
            utils.instance.create_virtualenv(env.virtualenv_path, env.user)

            print(green('\nPip installing requirements.'))
            utils.instance.pip_install_requirements(
                env.virtualenv_path,
                env.source_path,
                env.cache_path,
                env.log_path
            )

            print(green('\nCopying settings.py.'))
            utils.commands.copy(
                from_path = os.path.join(env.project_path, 'settings.py'),
                to_path = os.path.join(env.source_path, 'settings.py')
            )

            print(green('\nLinking media folder.'))
            utils.commands.create_symbolic_link(
                real_path = os.path.join(env.project_path, 'media'),
                symbolic_path = os.path.join(env.instance_path, 'media')
            )

            print(green('\nCollecting static files.'))
            utils.commands.django_manage(
                env.virtualenv_path,
                env.source_path,
                'collectstatic --link --noinput --verbosity=0 --traceback'
            )
        except:
            self.log(success=False)

            print(yellow('\nRemoving this instance from filesystem.'))
            utils.commands.delete(env.instance_path)

            abort(red('Deploy failed and was rolled back.'))

        # update database
        try:
            print(green('\nBacking up database at start.'))
            utils.instance.backup_database(
                env.virtualenv_path,
                env.scripts_path,
                os.path.join(env.backup_path, 'db_backup_start.sql')
            )

            print(green('\nSyncing database.'))
            utils.commands.django_manage(env.virtualenv_path, env.source_path, 'syncdb')

            print(green('\nMigrating database.'))
            utils.commands.django_manage(env.virtualenv_path, env.source_path, 'migrate')

            print(green('\nBacking up database at end.'))
            utils.instance.backup_database(
                env.virtualenv_path,
                env.scripts_path,
                os.path.join(env.backup_path, 'db_backup_end.sql')
            )
        except:
            self.log(success=False)

            print(yellow('\nRestoring database.'))
            utils.instance.restore_database(
                env.virtualenv_path,
                env.scripts_path,
                os.path.join(env.backup_path, 'db_backup_start.sql')
            )

            print(green('\nRemoving this instance from filesystem.'))
            utils.commands.delete(env.instance_path)

            abort(red('Deploy failed and was rolled back.'))

        print(green('\nUpdating instance symlinks.'))
        utils.instance.set_current_instance(env.project_path, env.instance_path)

        print(green('\nRestarting website.'))
        utils.commands.touch_wsgi(env.project_path)

        self.log(success=True)


class Rollback(RemoteTask):
    """ TASK: Rollback current instance to previous instance """

    name = 'rollback'

    def run(self, *args, **kwargs):

        self.stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        super(Rollback, self).run()

    def __call__(self):

        # check if rollback is possible
        if not exists(env.previous_instance_path):
            abort(red('No rollback possible. No previous instance found to rollback to.'))
        if not exists(os.path.join(env.backup_path, 'db_backup_start.sql')):
            abort(red('Could not find backupfile to restore database with.'))

        # start rollback
        try:
            print(green('\nRestoring database to start of this instance.'))
            utils.instance.restore_database(
                env.virtualenv_path,
                env.scripts_path,
                os.path.join(env.backup_path, 'db_backup_start.sql')
            )

            print(green('\nRemoving this instance and set previous to current.'))
            utils.instance.rollback(env.project_path)

            print(green('\nRestarting website.'))
            utils.commands.touch_wsgi(env.project_path)

            print(yellow('\nRemoving this instance from filesystem.'))
            utils.commands.delete(env.instance_path)

            self.log(success=True)

        except Exception, e:
            self.log(success=False)
            abort(red('Rollback failed: %s ' % e.message))


class Status(RemoteTask):
    """ INFO: Show status information for staging environment """

    name = 'status'

    def run(self, *args, **kwargs):

        self.stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        super(Status, self).run()

    def __call__(self):

        print(green('\nCurrent instance:'))
        print(utils.commands.read_link(env.current_instance_path))

        print(green('\nPrevious instance:'))
        print(utils.commands.read_link(env.previous_instance_path))

        print(green('\nFabric log:'))
        print(utils.commands.tail_file(os.path.join(env.log_path, 'fabric.log')))


class Media(RemoteTask):
    """ TASK: Download media files as archive from staging """

    name = 'media'

    def run(self, *args, **kwargs):

        self.stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        super(Media, self).run()

    def __call__(self):

        file_name = 'project_media.tar'
        cwd = os.getcwd()
        
        print(green('\nCompressing remote media folder.'))
        utils.commands.create_tarball(env.project_path, 'media', file_name)
        
        print(green('\nDownloading tarball.'))
        utils.commands.download_file(
            remote_path = os.path.join(env.project_path, file_name),
            local_path = os.path.join(cwd, file_name)
        )
        
        print(green('\nSaved media tarball to:'))
        print(os.path.join(cwd, file_name))


class Database(RemoteTask):
    """ TASK: Download database export from staging """

    name = 'database'

    def run(self, *args, **kwargs):

        self.stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        super(Database, self).run()

    def __call__(self):

        # TODO: timestamp as postfix
        file_name = 'db_backup.sql'
        cwd = os.getcwd()

        print(green('\nCreating backup.'))
        utils.instance.backup_database(
            env.virtualenv_path,
            env.scripts_path,
            os.path.join(env.backup_path, file_name)
        )

        print(green('\nDownloading and removing remote backup.'))
        utils.commands.download_file(
            remote_path = os.path.join(env.backup_path, file_name),
            local_path = os.path.join(os.getcwd(), file_name)
        )
        
        print(green('\nSaved backup to:'))
        print(os.path.join(cwd, file_name))