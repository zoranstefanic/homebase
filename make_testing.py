import sys
import os
sys.path.append('/home/zoran/django-projects/')
os.environ['DJANGO_SETTINGS_MODULE']='homebase.settings'
from homebase.crysalis.tests import *
from random import choice

s = Syncronize()
TEST_DIR = os.path.join(PROJECT_DIR,'testing')
DATA = os.path.join(TEST_DIR,'data')
LOG = os.path.join(TEST_DIR,'log')
for d in TEST_DIR, DATA, LOG:
	if not os.path.exists(d):
		print 'Making %s' %d
		os.mkdir(d)
	else:
		print '%s already exists, not making new one!' %d

def make_sample_data():
	random_ds_dirs = [choice(s.local_dirs) for i in range(3)]
	os.chdir(TEST_DIR)
	print os.getcwd()
	for d in random_ds_dirs:
		ds = Dataset(d)
		com =  'rsync -av --exclude-from=.rsync_exclude %s/ data/%s/' %(d, ds.name)
		print com
		os.system(com)
	print 'synchronizing log dir'
	log_sync = 'rsync -av /mnt/xcalibur/Xcalibur/log/crysalispro_ccdLOG* log/'
	os.system(log_sync)
	print 'All done!'

if __name__ == "__main__":
	make_sample_data()

