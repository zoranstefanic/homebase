#!/usr/bin/env python
import os
from homebase.settings import PROJECT_DIR

REMOTE_WIN 	= 'C:\\XcaliburData\\'				# This is a remote directory on the diffractometer where the original data goes

REMOTE		=	'/mnt/xcalibur'
REMOTE_MNT	= 	'/mnt/xcalibur/XcaliburData/'	# This is the same directory mount point on the server machine
SERVICE 	= 	'/mnt/xcalibur/Xcalibur/Service/'	# Service directory 
LOG_FILE_DIR = 	'/mnt/xcalibur/Xcalibur/log'		#Log file directory

LOCAL 		= 	'/media/usbdisk/xcalibur/XcaliburData'	# This is a backup directory on the server machine where the data are rsync-ed
DATA_DIR	=	'XcaliburData'
TMPDIR	=	os.path.join(PROJECT_DIR,'tmp')

DIRS_TO_SYNC=[	'Xcalibur/log',
				'Xcalibur/Service',
				'Xcalibur/CrysAlisINI',
				'../XcaliburData',
			]
BACKUP='/media/usbdisk/xcalibur'

class DirSync():
	def rsync_dir(self,d):
		dir1 = os.path.join(REMOTE,d)
		dir2 = os.path.join(BACKUP,d)
		print 'rsync -av --exclude=tmp/ -n %s/ %s' %(dir1,dir2)
		os.system('rsync -av --exclude=tmp/ -n %s/ %s' %(dir1,dir2))
		doit = raw_input('This was DRY RUN!\nDo you want to run for real? [Yes,No]')
		if doit=='Yes':
			os.system('rsync -av --exclude=tmp/  %s/ %s' %(dir1,dir2))
		else:
			pass
	
	def go(self):
		for d in DIRS_TO_SYNC:
			self.rsync_dir(d)

def win_to_local(path):
	"Converts remote windows path to local"
	path = path.replace('\\','/')[2:]
	win = REMOTE_WIN.replace('\\','/')[2:]
	path = os.path.relpath(path,win)
	return os.path.join(LOCAL,path)

def win_to_remote_mnt(path):
	"Converts remote windows path to local"
	path = path.replace('\\','/')[2:]
	win = REMOTE_WIN.replace('\\','/')[2:]
	path = os.path.relpath(path,win)
	return os.path.join(REMOTE_MNT,path)

def remote_mnt_to_local(path):
	"Converts locally mounted remote path to local"
	path = os.path.relpath(path,REMOTE_MNT)
	return os.path.join(LOCAL,path)
