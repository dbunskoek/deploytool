import os

import deployment.tasks as tasks


project_items = {
    'admin_email': 'info@example.com',
    'project_name': 'example',
    'hosts': ['192.168.1.666', ],
    'projects_root': os.path.join('/', 'path', 'to', 'projects'),
    'provisioning_user': 'sudoer',
}.items()

live_items = {
    'website_name': 'www.example.com',
    'project_name_prefix': 'l-',
    'environment': 'live',
}.items()

local_items = {
    'website_name': 'www.example.com.dev',
    'project_name_prefix': 'd-',
    'environment': 'local',
    'hosts': ['127.0.0.1', ],
}.items()

staging_items = {
    'website_name': 'subdomain.example.com',
    'project_name_prefix': 's-',
    'environment': 'staging',
}.items()


# hosts
staging = tasks.remote.RemoteHost(settings=dict(project_items + staging_items))
live = tasks.remote.RemoteHost(settings=dict(project_items + live_items))

# deployment
deploy = tasks.remote.Deployment()
rollback = tasks.remote.Rollback()
status = tasks.remote.Status()
database = tasks.remote.Database()
media = tasks.remote.Media()

# provisioning
setup = tasks.provision.Setup()
enable = tasks.provision.Enable()

# generic
list_tasks = tasks.generic.ListTasks()
