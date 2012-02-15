from datetime import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm
from fabric.operations import require
from fabric.tasks import Task
import os


class Setup(Task):
    """
    PROV - Provision project

        Sets up a new project on a remote server:
            - project user
            - database
            - database user
            - files & folders
            - apache & nginx configuration
            - optional .htpasswd security

        Requirements:
            - remote user with sudo rights
            - database root user with username/pwd equal to sudo user
            - your ssh public key on remote server or sudo pwd

        Usage:
            # copy sudo/db-root password to clipboard
            $ fab staging setup
            # answer prompted questions
            # paste pwd if challenged
    """

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
        # note that this user differs from local (e.g 'nick') or project user (e.g. 's-jouwomgeving')
        # make sure local user either knows remote password, or has its local public key on remote end
        print(green('\nConnecting with user %s ' % yellow(env.provisioning_user)))
        with settings(hide('running', 'stdout')):
            env.update({'user': env.provisioning_user})
            sudo('ls')  # aks for sudo NOW

        # prompt for start
        question = '\nStart provisioning of %s on %s?' % (env.project_name, env.environment)
        if not confirm(yellow(question)):
            abort(red('\nProvisioning cancelled.'))

        # create new project_user
        project_user = str.join('', [env.project_name_prefix, env.project_name])
        print(green('\nCreating project user: %s ' % project_user))

        try:
            # setup new user/pwd
            sudo('useradd %s' % project_user)
            sudo('passwd %s' % project_user)

            # setup SSH for user
            sudo('mkdir /home/%s/.ssh' % project_user)
            sudo('touch /home/%s/.ssh/authorized_keys' % project_user)
            sudo('chmod -R 700 /home/%s/.ssh' % project_user)
            sudo('chown -R %s:%s /home/%s/.ssh' % (project_user, project_user, project_user))

        except:
            # user already exists, ask if this user is available
            _args = (project_user, env.project_name, env.environment)
            question = '\nUser %s already exist. Use this user for %s on %s?' % _args

            if not confirm(yellow(question)):
                abort(red('Provisioning aborted because user %s is not available.' % project_user))

        # check for existing project paths, and abort if found
        if not exists(env.project_root):
            abort(red('Project root not found at: %s' % env.project_root))
        if exists(env.project_path):
            abort(red('Project path already exists at: %s' % env.project_path))

        # create folders
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

        # copy files
        print(green('\n\nCopying script files'))
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

        # create empty database (uses database root user)
        print(green('\nCreating empty database'))
        sudo('mysqladmin --user=%s -p create %s' % (env.provisioning_user, database_name))

        # create new database user with all schema privileges (uses database root user)
        print(green('\nCreating new database user'))
        _args = (env.provisioning_user, database_name, os.path.join(env.scripts_path, 'db_provision_user.sql'))
        sudo('mysql --user=%s -p --database="%s" < %s' % _args)

        # determine first available port # for vhost
        print(green('\nDetermining port # for project'))
        apache_conf_path = os.path.join('/', 'etc', 'httpd', 'conf.d')

        with settings(hide('stdout')):
            try:
                # grep vhosts => reverse list => awk top port #
                output = run('%s | %s | %s' % (
                    'grep -hr "NameVirtualHost" %s' % apache_conf_path,
                    'sort -r',
                    'awk \'{if (NR==1) { print substr($2,3) }}\''
                ))
                new_port_nr = int(output) + 1
            except:
                new_port_nr = '8001'

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

        remote_file = os.path.join(apache_conf_path, 'vhosts-%s.conf' % full_project_name)
        upload_template(
            filename = os.path.join(local_templates_path, 'apache_vhost.txt'),
            destination = remote_file,
            context = context,
            use_sudo = True
        )

        remote_file = os.path.join(nginx_conf_path, 'vhosts-%s.conf' % full_project_name)
        upload_template(
            filename = os.path.join(local_templates_path, 'nginx_vhost.txt'),
            destination = remote_file,
            context = context,
            use_sudo = True
        )

        # ask for optional setup of .htpasswd (used for staging environment)
        if confirm(yellow('\nSetup htpasswd for project?')):
            htpasswd_path = os.path.join(env.project_path, 'htpasswd')
            htpasswd = '%s%s' % (env.project_name, datetime.now().year)

            sudo('mkdir %s' % htpasswd_path)
            with cd(htpasswd_path):
                sudo('htpasswd -bc .htpasswd %s %s' % (env.project_name, htpasswd))

        # chown project for project user
        print(green('\nChowning %s for remote project user %s' % (project_user, env.project_path)))
        sudo('chown -R %s:%s %s' % (project_user, project_user, env.project_path))

        # display test results for webserver vhost config files
        print(green('\n\nTesting webserver configuration'))
        with settings(hide('warnings', 'stderr'), warn_only=True):
            sudo('/etc/init.d/httpd configtest')
            sudo('/etc/init.d/nginx configtest')

        # prompt for webserver restart 
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


class Keys(Task):
    """
    PROV - Enable devs for project by managing SSH keys

        Transfers a selected user's public SSH key to remote user's authorized key.
        This regulates access for admins without having to divulge project passwords.
    """

    name = 'keys'
    requirements = [
        'local_user',
        'project_name',
        'project_name_prefix',
        'provisioning_user',
    ]

    def run(self):

        # check if all required project and host settings are present in fabric environment
        [require(r) for r in self.requirements]

        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):

            # connect with provision user (who must have sudo rights on host)
            # note that this user differs from local (e.g 'nick') or project user (e.g. 's-jouwomgeving')
            # make sure local user either knows remote password, or has its local public key on remote end
            print(green('\nConnecting with user %s ' % yellow(env.provisioning_user)))
            env.update({'user': env.provisioning_user})

            # ask for sudo session up front
            sudo('ls')

            # call task implementation
            self()

    def __call__(self):

        project_user = env.project_name_prefix + env.project_name
        local_ssh_path = os.path.join('/', 'home', env.local_user, '.ssh')
        local_ssh_files = os.listdir(local_ssh_path)
        local_key_files = [f for f in local_ssh_files if f[-4:] == '.pub']
        selected_key_nr = 0
        remote_auth_keys = os.path.join('/', 'home', project_user, '.ssh', 'authorized_keys')

        if not local_key_files:
            abort(red('No public keys found in %s' % local_ssh_path))
        elif not exists(remote_auth_keys, use_sudo=True):
            abort(red('No authorized_keys found at %s' % remote_auth_keys))

        print(green('\nShowing local public keys in %s:' % local_ssh_path))
        for file in local_key_files:
            index = local_key_files.index(file)
            key_file = os.path.join(local_ssh_path, local_key_files[index])

            if self._is_key_authorized(remote_auth_keys, self._read_key(key_file)):
                print('[%s] %s (already enabled)' % (red(index), file))
            else:
                print('[%s] %s' % (green(index), file))

        print('\n[a] enable all local keys')
        print('[d] disable all remote keys')
        print('[s] show all remote authorized keys')
        selection = prompt(yellow('\nSelect option:'), default='a')

        if selection == 'a':
            for file in local_key_files:
                # grab key from selection (if multiple) or default (if single)
                key_file = os.path.join(local_ssh_path, file)
                key_to_transfer = self._read_key(key_file)
                self._transfer_key(remote_auth_keys, key_to_transfer)

        elif selection == 'd':
            print(green('\nDisabled all keys'))
            sudo('rm -f %s' % remote_auth_keys)
            sudo('touch %s' % remote_auth_keys)
            sudo('chmod -R 700 %s' % remote_auth_keys)
            sudo('chown %s:%s %s' % (project_user, project_user, remote_auth_keys))

        elif selection == 's':
            print(green('\nRemote authorized keys:'))
            print(sudo('cat %s' % remote_auth_keys) or red('[empty]'))

        else:
            try:
                key_file = os.path.join(local_ssh_path, local_key_files[int(selection)])
                key_to_transfer = self._read_key(key_file)
                self._transfer_key(remote_auth_keys, key_to_transfer)
            except:
                abort(red('Invalid selection'))

    def _transfer_key(self, remote_auth_keys, key_to_transfer):
        """ Appends key to supplied authorized_keys file """

        if not self._is_key_authorized(remote_auth_keys, key_to_transfer):
            print(green('\nTransferring key'))
            print(key_to_transfer)
            append(remote_auth_keys, key_to_transfer, use_sudo=True)

    def _read_key(self, key_file):
        """ Returns the content of a (public) SSH key-file """

        return '%s' % local('cat %s' % key_file, capture=True).strip()

    def _is_key_authorized(self, auth_keys_file, public_key):
        """ Checks if key is present in supplied authorized_keys file """

        authorized_keys = sudo('cat %s' % auth_keys_file)
        return bool(public_key in authorized_keys.split('\r\n'))
