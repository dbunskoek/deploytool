from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import *
import os

from commands import subprocess_popen


def transfer_source(upload_path):
    """ Archive source and upload/extract to/on remote server """

    tar_file = 'source.tar'
    local('git archive --format=tar --output=%s master' % tar_file)
    uploaded_files = put(tar_file, upload_path)

    if uploaded_files.succeeded:
        with cd(upload_path):
            run('tar -xf %s' % uploaded_files[0])
            run('rm -f ./%s' % tar_file)
        local('rm -f ./%s' % tar_file)


def create_tag(tag):

    local('git tag %s' % tag)
    local('git push --tags')


def delete_tag(tag):

    local('git tag -d %s' % tag)
    local('git push origin :refs/tags/%s' % tag)


def list_tags():
    """
    Uses subprocess to pipe the output of `git tag` to a variable.
    The tags are split to a list, converted to integers and reversed.
    """

    output = subprocess_popen(['git tag'])
    tags = [int(t) for t in output.split('\n') if t != '']
    tags.reverse()

    return tags


def list_commits(amount=10):
    """ Pipe git commit log to list """

    output = subprocess_popen(['git log master -n %d --pretty=format:%%H' % amount])
    return [c.strip() for c in output.split('\n') if c != '']


def get_branch_name():

    return subprocess_popen('git rev-parse --abbrev-ref HEAD').strip()


def get_head():

    return subprocess_popen('git rev-parse HEAD').strip()

