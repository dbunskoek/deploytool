import os

import deployment.tasks


settings_live = {
    'project_name': 'jouwomgeving',
    'project_name_prefix': 'l-',
    'environment': 'live',
    'hosts': ['192.168.1.666', ],
    'projects_root': os.path.join('/', 'var', 'www', 'vhosts'),
}
settings_local = {
    'project_name': 'jouwomgeving',
    'project_name_prefix': 'd-',
    'environment': 'local',
    'hosts': ['192.168.1.666', ],
    'projects_root': None,
}
settings_staging = {
    'project_name': 'jouwomgeving',
    'project_name_prefix': 's-',
    'environment': 'staging',
    'hosts': ['192.168.1.666', ],
    'projects_root': os.path.join('/', 'var', 'www', 'vhosts'),
}

# hosts
staging = deployment.tasks.remote.RemoteHost(project_settings=settings_staging)
live = deployment.tasks.remote.RemoteHost(project_settings=settings_live)

# tasks
deploy = deployment.tasks.remote.Deployment()
rollback = deployment.tasks.remote.Rollback()
status = deployment.tasks.remote.Status()
database = deployment.tasks.remote.Database()
media = deployment.tasks.remote.Media()
