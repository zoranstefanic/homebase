"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

## This part is former test.py file which needs to be ported 
# to use unittest as above
import os
import time
import pprint
import re
from django.template.defaultfilters import slugify
from synchronize import *
from models import *
from datetime import datetime
from itertools import groupby
pp = pprint.PrettyPrinter(indent=4).pprint

def extract_possible_sections_options(dirs,slugify=False):
	type_to_sections = {}
	for d in dirs: 
		ds = Dataset(d) 
		for ini in ds.ini_files():
			ini_file = IniFile(ini)
			type_to_sections.setdefault(ini_file.type,[])
			for sec in ini_file.sections():
				if slugify: sec = slugify(sec)
				if sec not in type_to_sections[ini_file.type]:
					type_to_sections[ini_file.type].append(sec)
	return type_to_sections

def test_frames_types():
	"""Testing of possible types of datasets
	"""
	s = Syncronize()
	for d in s.local_dirs:
		ds = Dataset(d)
		if '+' in ds.name: # This breaks the regexp so we escape
			ds.name = ds.name.replace('+',r'\+')
			print ds.name
		pre_patt = re.compile(r'(?P<pre>pre)_%s(_\d+){2}.img'%ds.name)
		ref_patt = re.compile(r'%sref(_\d+){4}.img'%ds.name)
		img_patt = re.compile(r'%s(_\d+){2}.img'%ds.name)
		imgs = map(os.path.basename,glob.glob(os.path.join(ds.d,'frames','*.img')))
		nums = [len(filter(pat.match,imgs)) for pat in pre_patt,img_patt,ref_patt]
		difference =  len(imgs) - nums[0] - nums[1] - nums[2]
		if not imgs:
			print '%100s    no images!' %ds.d
		if difference:
			print '%100s    pre: %5d img: %5d ref: %5d diff: %5d' %(ds.d,nums[0],nums[1],nums[2], difference)
		if not difference:
			print '%100s -- pre: %5d img: %5d ref: %5d diff: %5d' %(ds.d,nums[0],nums[1],nums[2], difference)

def test_full_pre_exp():
	s = Syncronize()
	out = open('test_full_pre_exp.out','w')
	for d in s.local_dirs:
		ds = Dataset(d)
		out.write('%-15s   %s\n' %(ds.type,d))
		print '%-15s   %s\n' %(ds.type,d)
	out.close()

def test_sections_options(ini_type,sec,opt):
	s = Syncronize()
	for d in s.local_dirs:
		ds = Dataset(d)
		inis = ds.ini_files()
		try:
			if ds.type == 'full':
				ds.get_section_option(ini_type,sec,opt)
			elif ds.type == 'pre':
				ds.get_section_option('pre_'+ini_type,sec,opt)
		except:
			print 'problem -->', ds.d

def dictinvert(d):
	"""Invert a dictionary"""
	inv = {}
	for k, v in d.iteritems():
		for i in v:
			keys = inv.setdefault(i, [])
			keys.append(k)
	return inv

# TESTS FOR LOGFILES
def timeline():
	"Utility function to test all posible scenarios"
	lines = open('timeline.tmp','r').readlines()
	s = ''
	for l in lines:
		if not l.startswith('DCINFO'):
			s += '%10s' %l.strip()
		else:
			print s
			s = l.strip()

def test_parse():
	ld = LogDir()
	for log in ld.log_files():
		log = CcdLogFile(log)
		log.parse()
	#log.extract_dcinfo()

def test_dcinfo():
	ld = LogDir()
	for log in ld.log_files():
		log = CcdLogFile(log)
		log.extract_dcinfo()

def group_datasets_by(datasets,what):
	out = open('%s.tmp' %what,'w')
	datasets= sorted(datasets, key= lambda a: a.__getattribute__(what))
	gbo = groupby(datasets, lambda a: a.__getattribute__(what))
	for key, dc in gbo:
		s = "%-100s" %key
		for d in dc:
			s += '%-25s' %d.__getattribute__('start') 
		out.write(s+'\n')
	out.close()

		
if __name__ == '__main__':
	test_all_datasets()
