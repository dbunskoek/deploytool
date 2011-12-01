from hosts.base import FabricEnvironmentUpdater


class LiveHost(FabricEnvironmentUpdater):
    """ Live settings """

    settings = {
        'environment': 'live',
        'hosts': ['lithium-oxide', ],
    }
