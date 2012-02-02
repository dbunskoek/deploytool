from datetime import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm
from fabric.operations import require
from fabric.tasks import Task
import os


class Setup(Task):
    """ Provision project """

    name = 'setup'
    requirements = [
        'admin_email',
        'cache_path',
        'current_instance_path',
        'database_name',
        'environment',
        'log_path',
        'local_user',
        'media_path',
        'project_name',
        'project_name_prefix',
        'project_path',
        'projects_root',
        'provisioning_user',
        'real_fabfile',
        'scripts_path',
        'website_name',
    ]

    def run(self):

        # check if all required project and host settings are present in fabric environment
        [require(r) for r in self.requirements]

        # connect with provision user (who must have sudo rights on host)
        env.update({'user': env.provisioning_user})

        # prompt for start
        question = '\nStart provisioning of %s on %s?' % (env.project_name, env.environment)
        if not confirm(yellow(question)):
            abort(red('\nProvisioning cancelled.'))

        # creating project_user
        project_user = str.join('', [env.project_name_prefix, env.project_name])
        print(green('\nCreating project user: %s ' % project_user))

        try:
            with settings(hide('warnings', 'stderr'), warn_only=True):
                sudo('adduser %s' % project_user)
        except:
            # user already exists, ask if this user is available
            _args = (remote_user_name, env.project_name, env.environment)
            question = '\nUser %s already exist. Use this user for %s on %s?' % _args

            if not confirm(yellow(question)):
                abort(red('Provisioning aborted because user %s is not available.' % remote_user_name))

        # check project paths
        if not exists(env.project_root):
            abort(red('Project root not found at: %s' % env.project_root))
        if exists(env.project_path):
            abort(red('Project path already exists at: %s' % env.project_path))

        # create folders for project
        print(green('\nCreating folders'))
        folders_to_create = [
            env.project_path,
            env.cache_path,
            env.log_path,
            env.media_path,
            env.scripts_path,
        ]

        for folder in folders_to_create:
            sudo('mkdir %s' % folder)

        # copy script files
        print(green('\nCopying script files'))
        local_scripts_path = os.path.join(os.path.dirname(env.real_fabfile), 'deployment', 'scripts')
        files_to_copy =  os.listdir(local_scripts_path)

        for file_name in files_to_copy:
            put(
                local_path = os.path.join(local_scripts_path, file_name),
                remote_path = os.path.join(env.scripts_path, file_name),
                use_sudo = True
            )

        # ask user input for template based file creation
        print(yellow('\nProvide info for file creation:'))
        local_templates_path = os.path.join(os.path.dirname(env.real_fabfile), 'deployment', 'templates')
        full_project_name = str.join('', [env.project_name_prefix, env.project_name])
        database_name = prompt('Database name: ', default=full_project_name)
        database_user = prompt('Database username: ', default=full_project_name)
        database_pass = prompt('Database password: ', validate=self._validate_password)

        files_to_create = [
            {'template': 'settings_py.txt', 'file': 'settings.py', },
            {'template': 'credentials_py.txt', 'file': 'scripts/credentials.py', },
            {'template': 'django_wsgi.txt', 'file': 'django.wsgi', },
            {'template': 'db_provision_user_sql.txt', 'file': 'scripts/db_provision_user.sql', },
        ]

        context = {
            'project_name': env.project_name,
            'current_instance_path': env.current_instance_path,
            'cache_path': env.cache_path,
            'database_name': database_name,
            'username': database_user,
            'password': database_pass,
        }

        # create files from templates (using fabric env and user input)
        print(green('\nCreating project files'))
        for file_to_create in files_to_create:
            upload_template(
                filename = os.path.join(local_templates_path, file_to_create['template']),
                destination = os.path.join(env.project_path, file_to_create['file']),
                context = context,
                use_sudo = True
            )

        # create empty database
        print(green('\nCreating empty database'))
        sudo('mysqladmin --user=%s -p create %s' % (env.provisioning_user, database_name))

        # create new database user with all schema privileges
        print(green('\nCreating new database user'))
        _args = (env.provisioning_user, database_name, os.path.join(env.scripts_path, 'db_provision_user.sql'))
        sudo('mysql --user=%s -p --database="%s" < %s' % _args)

        # determine first available port # for vhost
        #   TODO: rewrite grep statement to return last port
        print(green('\nDetermining port # for project'))
        apache_conf_path = os.path.join('/', 'etc', 'httpd', 'conf.d')

        with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
            vhosts = run('grep -hr "NameVirtualHost" %s | sort' % apache_conf_path)

        ports = [vhost[-4:] for vhost in vhosts.strip().split('\n')]
        ports.reverse()
        new_port_nr = int(ports[0]) + 1
        print 'Port %s will be used for this project' % yellow(new_port_nr)

        # create apache/nginx conf files
        print(green('\nCreating vhost conf files'))
        nginx_conf_path = os.path.join('/', 'etc', 'nginx', 'conf.d')
        context = {
            'port_number': new_port_nr,
            'current_instance_path': env.current_instance_path,
            'website_name': env.website_name,
            'project_name': env.project_name,
            'project_name_prefix': env.project_name_prefix,
            'project_path': env.project_path,
            'log_path': env.log_path,
            'admin_email': env.admin_email,
            'project_user': project_user,
        }

        upload_template(
            filename = os.path.join(local_templates_path, 'apache_vhost.txt'),
            destination = os.path.join(apache_conf_path, 'vhosts-%s.conf' % full_project_name),
            context = context,
            use_sudo = True
        )
        upload_template(
            filename = os.path.join(local_templates_path, 'nginx_vhost.txt'),
            destination = os.path.join(nginx_conf_path, 'vhosts-%s.conf' % full_project_name),
            context = context,
            use_sudo = True
        )

        # confirm setup htpasswd
        if confirm(yellow('\nSetup htpasswd for project?')):
            htpasswd_path = os.path.join(env.project_path, 'htpasswd')
            htpasswd = '%s%s' % (env.project_name, datetime.now().year)

            sudo('mkdir %s' % htpasswd_path)
            with cd(htpasswd_path):
                sudo('htpasswd -bc .htpasswd %s %s' % (env.project_name, htpasswd))

        # chown project for project user
        print(green('\nChowning %s for remote project user %s' % (project_user, env.project_path)))
        sudo('chown -R %s:%s %s' % (project_user, project_user, env.project_path))

        # testing webserver vhost config files
        print(green('\nTesting webserver configuration'))
        with settings(hide('warnings', 'stderr'), warn_only=True):
            sudo('/etc/init.d/httpd configtest')
            sudo('/etc/init.d/nginx configtest')

        # confirm for webserver restart
        if confirm(yellow('\nOK to restart webserver?')):
            sudo('/etc/init.d/httpd restart')
            sudo('/etc/init.d/nginx restart')
        else:
            print(magenta('Website will be available when webserver is restarted.'))

    def _validate_password(self, password):
        """ Validator for input prompt when asking for password """

        min_length_required = 8

        if len(password.strip()) < min_length_required:
            raise Exception(red('Please enter a valid password of at least %s characters' % min_length_required))

        return password.strip()

