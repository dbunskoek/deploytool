import os
import sys
from setuptools import setup, find_packages

version = __import__('deploytool').__version__

if sys.argv[-1] == 'publish': # upload to pypi
    os.system("python setup.py register sdist upload")
    print "You probably want to also tag the version now:"
    print "  git tag -a %s -m 'version %s'" % (version, version)
    print "  git push --tags"
    sys.exit()

setup(
    name='deploytool',
    version=version,
    license='Apache License, Version 2.0',

    install_requires=[
        'fabric>=1.2.2',
    ],

    description='Deploytool - a Django Fabric deploytool',
    long_description=open('README.rst').read(),

    author='Nick Badoux',
    author_email='nbadoux@leukeleu.nl',

    url='https://github.com/leukeleu/deploytool',
    download_url='https://github.com/leukeleu/deploytool/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
