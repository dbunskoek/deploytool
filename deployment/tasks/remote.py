from datetime import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm
from fabric.operations import require
from fabric.tasks import Task
import os

import deployment.utils as utils


class RemoteHost(Task):
    """ HOST """

    requirements = [
        'admin_email',
        'website_name',
        'environment',
        'hosts',
        'project_name',
        'project_name_prefix',
        'projects_root',
    ]

    def __init__(self, *args, **kwargs):

        # use environment as task name
        self.name = kwargs['settings']['environment']

        # save project settings in instance
        self.settings = kwargs['settings']

    def run(self):

        # update fabric environment for project settings
        env.update(self.settings)

        # check if all required project settings are present in fabric environment
        [require(r) for r in self.requirements]

        project_name = '%s%s' % (env.project_name_prefix, env.project_name)
        project_path = os.path.join(env.projects_root, project_name)

        print(green('\nInitializing fabric environment for %s.' % magenta(self.name)))
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
            datetime.today().strftime('%Y-%m-%d %H:%M'),
            self.name,
            result,
            env.environment,
            env.local_user,
            self.stamp
        )

        append(os.path.join(env.log_path, 'fabric.log'), message)

    def run(self, *args, **kwargs):
        """ Hide output, update fabric env, run task """

        # hide fabric output
        with settings(hide('running', 'stdout'), warn_only=True):

            # check if HOST task was run before this task
            if not hasattr(env, 'current_instance_path'):
                message = str.join(' ', [
                    red('\nRun a HOST task before running this remote task (e.g. `fab staging deploy`).\n'),
                    'Use `fab -l` to see a list of all available tasks.\n',
                    'Use `fab -d %s` to see this task\'s details.\n' % self.name,
                ])
                abort(message)

            # load current instance unless task already provided something else
            if not hasattr(self, 'stamp'):
                self.stamp = utils.instance.get_instance_stamp(env.current_instance_path)

            # check if all required HOST settings are present in fabric environment
            [require(r) for r in self.requirements]

            # update fabric environment for instance settings
            instance_path = os.path.join(env.project_path, self.stamp)
            env.update({
                'backup_path': os.path.join(instance_path, 'backup'),
                'instance_stamp': self.stamp,
                'instance_path': instance_path,
                'source_path': os.path.join(instance_path, env.project_name),
                'virtualenv_path': os.path.join(instance_path, 'env'),
            })

            # finally, run the task implementation!
            self()


class Deployment(RemoteTask):
    """
    REMO - Deploy new instance

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
        """ 
        Load instance from CLI kwargs

            default => deploy by HEAD for current branch by default
            commit  => deploy by commit SHA1 ID
            branch  => deploy by HEAD for branch
        """

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):

            # deploy by local commit
            if kwargs.has_key('commit'):
                self.stamp = kwargs['commit']

            # deploy by HEAD for branch
            elif kwargs.has_key('branch'):
                self.stamp = utils.source.get_commit_id(kwargs['branch'])

            # deploy by local HEAD for local current branch
            else:
                self.stamp = utils.source.get_head()
                _args = (utils.source.get_branch_name(), self.stamp)
                question = '\nDeploy branch %s at commit %s?' % _args

                if not confirm(yellow(question)):
                    abort(red('Aborted deployment. Run `fab -d %s` for options.' % self.name))

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
                symbolic_path = os.path.join(env.source_path, 'media')
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

            with settings(show('stdout')):
                print(green('\nSyncing database.'))
                utils.commands.django_manage(env.virtualenv_path, env.source_path, 'syncdb')
                print('')

                print(green('\nMigrating database.'))
                utils.commands.django_manage(env.virtualenv_path, env.source_path, 'migrate')
                print('')

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
        self.prune_instances()


    def prune_instances(self):
        """ Find old instances and remove them to free up space """

        old_instances = utils.instance.get_obsolete_instances(env.project_path)

        for instance in old_instances:
            is_current = bool(utils.instance.get_instance_stamp(env.current_instance_path) == instance)
            is_previous = bool(utils.instance.get_instance_stamp(env.previous_instance_path) == instance)

            if not (is_current or is_previous):
                utils.commands.delete(os.path.join(env.project_path, instance))

        if len(old_instances) > 0:
            print(green('\nThese old instances were removed from remote filesystem:'))
            print(old_instances)


class Rollback(RemoteTask):
    """ REMO - Rollback current instance to previous instance """

    name = 'rollback'

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

            print(green('\nRemoving this instance from filesystem.'))
            utils.commands.delete(env.instance_path)

            self.log(success=True)

        except Exception, e:
            self.log(success=False)
            abort(red('Rollback failed: %s ' % e.message))


class Status(RemoteTask):
    """ REMO - Show status information for remote host """

    name = 'status'

    def __call__(self):

        print(green('\nCurrent size of entire project:'))
        print(utils.commands.get_folder_size(env.project_path))

        print(green('\nCurrent instance:'))
        current_instance = utils.commands.read_link(env.current_instance_path)
        if current_instance != env.current_instance_path:
            print(current_instance)
        else:
            print(red('[none]'))

        print(green('\nPrevious instance:'))
        previous_instance = utils.commands.read_link(env.previous_instance_path)
        if previous_instance != env.previous_instance_path:
            print(previous_instance)
        else:
            print(red('[none]'))

        print(green('\nFabric log:'))
        if exists(os.path.join(env.log_path, 'fabric.log')):
            print(utils.commands.tail_file(os.path.join(env.log_path, 'fabric.log')))
        else:
            print(red('[empty]'))


class Media(RemoteTask):
    """ REMO - Download media files (as archive) """

    name = 'media'

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
    """ REMO - Download database (as sqldump) """

    name = 'database'

    def __call__(self):

        timestamp = datetime.today().strftime('%y%m%d%H%M')
        file_name = '%s_%s.sql' % (env.database_name, timestamp)
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
