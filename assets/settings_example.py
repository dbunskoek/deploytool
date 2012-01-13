# Fabric deployment default settings
DEPLOYMENT = {
    'project_name': None,           # 'PROJECTNAME',
    'host_staging': None,           # ['192.168.1.666', ],
    'host_live': None,              # ['192.168.1.666', ],
    'project_root_staging': None,   # os.path.join('/', 'var', 'www', 'vhosts'),
    'project_root_live': None,      # os.path.join('/', 'var', 'www', 'vhosts'),
    'project_vcs_repo': None,       # 'git@github.com:leukeleu/PROJECTNAME.git',
    'project_vcs_wget': None,       # 'https://github.com/leukeleu/PROJECTNAME/tarball/',
}
