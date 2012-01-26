from fabric.api import *
from fabric.colors import *
from fabric.tasks import Task

from deployment.hosts import RemoteHost


class StagingTask(Task):
    """ Base class for Task providing link to Host """

    host = None
    name = None

    def __init__(self, *args, **kwargs):
        """ Link task to host """

        self.host = RemoteHost(project_settings=kwargs['project_settings'])

    def run(self, *args, **kwargs):
        """ Execute task (quietly by default) """

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            self(*args, **kwargs)

    def __call__(self):
        """ Task implementation """

        raise NotImplementedError


class Deployment(StagingTask):
    """
    Deploy new instance to staging

        fab staging.deploy
        fab staging.deploy:branch=my-branch
        fab staging.deploy:commit=1ec9d293ce54647df7f15ee7c0295b8eb2a5cbef
    """

    name = 'deploy'

    def __call__(self, *args, **kwargs):

        print(yellow('\nStart task - deploy to staging'))

        # check for params
        instance = self.host.instance
        stamp = instance.create_stamp(
            branch = kwargs.get('branch', 'master'),
            commit = kwargs.get('commit', None)
        )

        # load instance and check if all is well for deployment
        self.host.load_instance(stamp=stamp)
        instance.check_deploy()

        # deploy source
        try:
            instance.create_folders()
            instance.deploy_source()
            instance.create_virtualenv()
            instance.copy_settings_file()
            instance.link_media_folder()
            instance.collect_static_files()
        except:
            instance.log(self.name, success=False)
            instance.delete()
            abort(red('Deploy failed and was rolled back.'))

        # update database
        try:
            instance.update_database()
        except:
            instance.log(self.name, success=False)
            instance.restore_database()
            instance.delete()
            abort(red('Deploy failed and was rolled back.'))

        # notify webserver
        instance.set_current()
        self.host.reload()

        instance.log(self.name)


class Rollback(StagingTask):
    """ Rollback current instance to previous instance """

    name = 'rollback'

    def __call__(self):

        print(yellow('\nStart task - rollback to previous'))

        self.host.load_current_instance()
        self.host.instance.check_rollback()

        try:
            self.host.instance.rollback()
            self.host.reload()
            self.host.instance.delete()
            self.host.instance.log(self.name)

        except Exception, e:
            self.host.instance.log(self.name, success=False)
            abort(red('Rollback failed: %s ' % e.message))
