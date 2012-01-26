from fabric.api import settings, hide
from fabric.colors import *
from fabric.tasks import Task

from deployment.hosts import RemoteHost


class RemoteTask(Task):
    """ Base class for Task providing link to Host """

    host = None
    name = None
    text = None

    def __init__(self, *args, **kwargs):
        """ Link task to host """

        self.host = RemoteHost(project_settings=kwargs['project_settings'])

    def run(self, *args, **kwargs):
        """ Execute task (quietly by default) """

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            print(magenta(self.pretty_text()))
            self(*args, **kwargs)

    def pretty_text(self):
        """ Returns boxed task-title from self.text """

        title = '| TASK - %s |' % self.text
        line = str.join('-', ['' for s in range(len(title)-1)])

        return '\n+%s+\n%s\n+%s+\n' % (line, title, line)

    def __call__(self):
        """ Task implementation """

        raise NotImplementedError