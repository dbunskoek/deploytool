from fabric.api import run
from fabric.colors import red
from fabric.contrib.files import local, put
import os

from utils.commands import subprocess_popen


def transfer_source(download_url, upload_path, tag='master', tar_file='source.tar.gz'):
    """ Download source tarball from VCS and upload/extract to/on remote server """

    local('wget %s%s -O ./%s' % (download_url, tag, tar_file))
    uploaded_files = put(tar_file, upload_path)

    if uploaded_files.succeeded:
        run('tar -zxf %s --strip=1 -C %s' % (uploaded_files[0], upload_path))
        run('rm -f %s' % os.path.join(upload_path, tar_file))
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
