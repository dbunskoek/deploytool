from fabric.api import hide, settings
from fabric.colors import *
from fabric.tasks import Task

from deployment.hosts.staging.host import StagingHost


class StagingTask(Task):
    """ Base class for Task providing link to Host """

    host = None
    name = None

    def __init__(self, *args, **kwargs):
        """ Link task to host """

        self.host = StagingHost(project_settings=kwargs['project_settings'])

    def run(self, *args, **kwargs):
        """ Execute task (quietly by default) """

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            self()

    def __call__(self):
        """ Task implementation """

        raise NotImplementedError


class Deployment(StagingTask):
    """ Deploys latest source as new instance """

    name = 'deploy'

    def __call__(self):

        print(yellow('\nStart task - deploy to staging'))

        # check requirements
        instance = self.host.instance
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
            instance.delete()
            abort(red('Deploy failed and was rolled back.'))
        
        # update database
        try:
            instance.update_database()
        except:
            instance.restore_database()
            instance.delete()
            abort(red('Deploy failed and was rolled back.'))
        
        # notify webserver
        instance.set_current()
        self.host.reload()


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

        except Exception, e:
            abort(red('Rollback failed: %s ' % e.message))
