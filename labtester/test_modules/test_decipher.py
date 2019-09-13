#!/usr/bin/python

import os
import sys


def test_decipher(text, hostname):
	cmds = []
	for line in text.splitlines():
		run_what = list(filter(None, line.split(":")))
		if run_what[0] == "loony":
			if len(run_what) == 2:
				cmds.append("loony -H {} clear attribute {}".format(hostname, run_what[1]))
			elif len(run_what) == 3:
				cmds.append("loony -H {} set attribute {}:{}".format(hostname, run_what[1], run_what[2]))
		elif run_what[0] == "ipmi":
			cmds.append("ipmitool -H {}.ipmi.twttr.net -U root -P root {}".format(hostname, run_what[1]))
	cmds.append("loony -H {} set attribute validation_status:TLT_STARTING".format(hostname))
	return cmds

test = sys.argv[1]
hostname = sys.argv[2]
try:
	run = sys.argv[3]
except:
	run = "dryrun"

cmds = test_decipher(test, hostname)

if run == "run":
	for i in cmds:
		print(i)
		os.system(i)
		
else:
	print('\n'.join([i for i in cmds[0:]]))

