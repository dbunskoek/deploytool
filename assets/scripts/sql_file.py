import subprocess
import sys

from credentials import *


command = 'mysql --user=%s --password=%s --database=%s < %s' % (
	username,
	password,
	database,
	sys.argv[1]
)

subprocess.call(command, shell=True)