from fabric.colors import *
from fabric.tasks import Task

from deployment.hosts.staging.host import StagingHost


class StagingTask(Task):
    """ Base class for Task providing link to Host """

    def __init__(self, *args, **kwargs):

        self.host = StagingHost(project_settings=kwargs['project_settings'])


class Deployment(StagingTask):
    """ Deploys latest source as new instance """

    name = 'deploy'

    def run(self):

        print(yellow('\nStart task - deploy to staging'))

        try:
            self.host.instance.deploy()

            try:
                self.host.instance.update_database()

            except SystemExit, e:
                print(red('Update database failed. Rolling back deployment ...'))
                self.host.instance.restore_database()
                self.host.instance.delete()

            self.host.instance.set_current()
            self.host.reload()

        except SystemExit, e:
            print(red('Create instance failed. Rolling back deployment ...'))
            self.host.instance.delete()


class Rollback(StagingTask):
    """ Rollback current instance to previous instance """

    name = 'rollback'

    def run(self):

        print(yellow('\nStart task - rollback to previous'))
        self.host.load_current_instance()
        
        try:
            self.host.instance.rollback()
            self.host.reload()
            self.host.instance.delete()

        except SystemExit, e:
            print(red('Rollback failed: %s ' % e.message))
