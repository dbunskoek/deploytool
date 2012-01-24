import subprocess
import sys

from credentials import *


command = 'mysqladmin --user=%s --password=%s create %s' % (
	username,
	password,
	database
)

subprocess.call(command, shell=True)