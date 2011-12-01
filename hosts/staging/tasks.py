from fabric.api import env
from fabric.tasks import Task

from hosts.staging.host import StagingHost
import utils


class StagingTaskBase(Task):
    """ Base class for Task providing link to Host """

    host = None

    def __init__(self, *args, **kwargs):

        self.host = StagingHost(*args, **kwargs)


class Deployment(StagingTaskBase):
    """ Deploys latest source as new instance """

    name = 'deploy'

    def run(self):

        try:
            self.host.instance.create(env)
        except SystemExit:
            self.host.instance.delete(env)

        try:
            self.host.instance.update_database(env)
        except SystemExit:
            self.host.instance.restore_database(env)
            self.host.instance.delete(env)

        self.host.instance.update_webserver(env)


class Rollback(StagingTaskBase):
    """ Rollback current instance to previous instance """

    name = 'rollback'

    def run(self):

        raise NotImplementedError
