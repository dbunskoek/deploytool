from fabric.api import env

import hosts.live.tasks as live
import hosts.local.tasks as local
import hosts.staging.tasks as staging
import settings


# Create available tasks
staging.deploy = staging.Deployment(project_settings=settings.defaults)
staging.rollback = staging.Rollback(project_settings=settings.defaults)
