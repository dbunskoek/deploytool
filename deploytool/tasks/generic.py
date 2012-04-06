from datetime import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm
from fabric.operations import require
from fabric.tasks import Task
import os

import deploytools.utils as utils


class ListTasks(Task):
    """ GENE - Parses `fab --list` and displays custom categorized list """

    name = 'list'
    categories = {
        'PROV': 'Provisioning',
        'REMO': 'Deployment',
        'HOST': 'Environments',
    }

    def run(self):

        # hide all fabric output
        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):

            # grab output from fabric's task list
            output = local('fab --list', capture=True)
            # filter for indented tasks and split to list
            lines = [t for t in output.split('\n') if t != '' and t[0].isspace()]
            task_list = []

            # create custom task list from fabric list output
            for line in lines:
                words = str.split(line)
                _name = words[0]
                _category = words[1]
                _description = str.join(' ', words[3:])

                if len(words) > 1 and _category in self.categories.keys():
                    task_list.append({
                        'name': _name,
                        'category': _category,
                        'description': _description,
                    })

            # display pretty custom categorized list
            print(yellow('\n+-----------------+\n| Available tasks |\n+-----------------+'))
            task_list.sort()
            current_category = ''

            for task in task_list:
                if task['category'] != current_category:
                    current_category = task['category']
                    print(green('  \n  %s' % self.categories[current_category]))
                print('    %(name)s\t%(description)s' % task)
