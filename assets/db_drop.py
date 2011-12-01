import subprocess
import sys

from credentials import *


command = 'mysqladmin -f --user=%s --password=%s drop %s' % (
	username,
	password,
	database	
)

subprocess.call(command, shell=True)