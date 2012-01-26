from fabric.api import settings, hide
from fabric.tasks import Task

from deployment.hosts import RemoteHost


class RemoteTask(Task):
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