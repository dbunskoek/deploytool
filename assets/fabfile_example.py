import os

import deployment.live.tasks as live
import deployment.local.tasks as local
import deployment.staging.tasks as staging


# project settings per environment
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

# available tasks
staging.deploy = staging.Deployment(project_settings=settings_staging)
staging.database = staging.Database(project_settings=settings_staging)
staging.media = staging.Media(project_settings=settings_staging)
staging.rollback = staging.Rollback(project_settings=settings_staging)
staging.status = staging.Status(project_settings=settings_staging)