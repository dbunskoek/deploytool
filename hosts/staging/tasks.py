from fabric.tasks import Task

from hosts.staging.host import StagingHost


class StagingTaskBase(Task):
    """ Base class for Task providing link to Host """

    def __init__(self, *args, **kwargs):

        self.host = StagingHost(project_settings=kwargs['project_settings'])


class Deployment(StagingTaskBase):
    """ Deploys latest source as new instance """

    name = 'deploy'

    def run(self):

        instance = self.host.instance

        try:
            instance.deploy()
        except SystemExit:
            instance.delete()

        try:
            instance.update_database()
        except SystemExit:
            instance.restore_database()
            instance.delete()

        instance.set_current()
        self.host.reload()


class Rollback(StagingTaskBase):
    """ Rollback current instance to previous instance """

    name = 'rollback'

    def run(self):

        raise NotImplementedError
