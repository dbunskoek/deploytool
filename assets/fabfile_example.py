# Copy & rename to your project root as fabfile.py

import os

# import tasks for hosts
import deployment.hosts.staging.tasks as staging


# project settings
settings = {
    'project_name': 'jouwomgeving',
    'host_staging': ['192.168.1.666', ],
    'host_live': ['192.168.1.666', ],
    'project_root_staging': os.path.join('/', 'var', 'www', 'vhosts'),
    'project_root_live': os.path.join('/', 'var', 'www', 'vhosts'),
}

# available tasks
staging.deploy = staging.Deployment(project_settings=settings)
staging.rollback = staging.Rollback(project_settings=settings)
