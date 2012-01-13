import hosts.staging.tasks as staging
import sys; sys.path.append('..')
import settings_default


# django project settings
PROJECT_SETTINGS = getattr(settings_default, 'DEPLOYMENT')

# available tasks
staging.deploy = staging.Deployment(project_settings=PROJECT_SETTINGS)
staging.rollback = staging.Rollback(project_settings=PROJECT_SETTINGS)
