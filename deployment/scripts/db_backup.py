import subprocess
import sys

from credentials import *


command = 'mysqldump --user="%s" --password="%s" "%s" > %s' % (
	username,
	password,
	database,
	sys.argv[1]
)

subprocess.call(command, shell=True)