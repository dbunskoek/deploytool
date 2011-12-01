from hosts.base import FabricEnvironmentUpdater


class LocalHost(FabricEnvironmentUpdater):
    """ Local settings """

    settings = {
        'environment': 'local',
        'hosts': ['lithium-oxide', ],
    }
