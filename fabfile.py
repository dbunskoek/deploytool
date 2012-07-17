import os

import deploytool.tasks as tasks


project_items = {
    'admin_email': 'info@example.com',
    'project_name': 'example',
    'provisioning_user': 'sudoer',
    'projects_root': os.path.join('/', 'path', 'to', 'projects'),
    'hosts': ['192.168.1.1', ],
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

live_items = {
    'website_name': 'www.example.com',
    'project_name_prefix': 'l-',
    'environment': 'live',
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
keys = tasks.provision.Keys()

# generic
list_tasks = tasks.generic.ListTasks()
