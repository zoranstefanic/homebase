#!/usr/bin/python2.6 
import sys
import re
import os
import time
import shutil
import glob
import pickle
import ConfigParser
from random import choice
from datetime import datetime, timedelta

# Django specific imports
sys.path.append('/home/zoran/django-projects/')
os.environ['DJANGO_SETTINGS_MODULE']='homebase.settings'
from homebase.experiments.models import Experiment
from homebase.settings import EXPERIMENTS_DIR
from django.db.models import Q
from django.contrib.auth.models import User
from paths import *


# Time format string used in Xcalibur ini and log files
TIMEFMT1 = '"%a %b %d %H:%M:%S %Y"'

class Dataset:
	"""	
	This class is initialized with one directory that
	contains one complete data collection. This directory
	may be anywhere in the REMOTE_MNT directory tree. It is characterized 
	by the presence of "frames" and 'log' subdirectories. 
	"""
	def __init__(self,d):
		"The only input is the directory"
		self.d = d
		self.name = os.path.basename(self.d)
		self.files = [f for f in os.listdir(self.d) if os.path.isfile(os.path.join(self.d,f))]
		self.dirs = [f for f in os.listdir(self.d) if os.path.isdir(os.path.join(self.d,f))]
		self.ini_types = self.ini_types()
		self.type = self.set_type()
	
	def ini_files(self):
		"""Filters only *.ini files"""
		inis = glob.glob(os.path.join(self.d,'*.ini'))
		if 'expinfo' in self.dirs:
			inis += glob.glob(os.path.join(self.d,'expinfo','*.ini'))
		return inis

	def dat_files(self):
		"""Filters only *.dat files"""
		dats = glob.glob(os.path.join(self.d,'*.dat'))
		if 'plots_red' in self.dirs:
			dats += glob.glob(os.path.join(self.d,'plots_red','*.dat'))
		return dats

	def ini_types(self):
		return [IniFile(ini).type for ini in self.ini_files()]
	
	def get_ini_file(self,type):
		inis = [ini for ini in self.ini_files() if IniFile(ini).type == type]
		if len(inis) == 1:
			return inis[0]
		else:
			return ''

	def get_dat_file(self,type):
		dats = [dat for dat in self.dat_files() if DatFile(dat).type == type]
		if len(dats) == 1:
			return dats[0]
		else:
			return ''

	def get_section_option(self,ini_type,section,option):
		if not ini_type in self.ini_types:
			print 'No %s in %s' %(ini_type, self.d)
			return None
		parser = IniFile(self.get_ini_file(ini_type)).parser()
		if not section in parser.sections():
			return None
		if not option in parser.options(section):
			return None
		else:
			return parser.get(section,option) 
	
	def get_cell(self):
		try:
			if self.type == 'pre':
				cell = self.get_section_option('pre_crystal','Lattice','constants plus vol').split()
			else:
				cell = self.get_section_option('crystal','Lattice','constants plus vol').split()
			return cell
		except:
			return [None]*7

	def get_user(self):
		try:
			if self.type == 'pre':
				user = self.get_section_option('pre_rrp','User','name')
			else:
				user = self.get_section_option('rrp','User','name')
			return user.strip('"')
		except:
			return None

	def get_comment(self):
		try:
			if self.type == 'pre':
				comment = self.get_section_option('pre_rrp','Client comment','comment')
			else:
				comment = self.get_section_option('rrp','Client comment','comment')
			return comment
		except:
			return None

	def get_datetime(self,which_time):
		if self.type == 'pre':
			dati = self.get_section_option('pre_datacoll','Date',which_time)
		elif self.type in ('full','full_no_pre','other','powder'):
			dati = self.get_section_option('datacoll','Date',which_time)
		if dati:
			return datetime.strptime(dati,TIMEFMT1)
		else:
			return None

	def get_space_group(self):
		if self.type == 'pre':
			ini_type = 'pre_datared'
		elif self.type == 'full':
			ini_type = 'datared'
		try:
			sg	= self.get_section_option(ini_type,'Space group','cifdescriptor')
			return sg.strip('"')
		except:
			return None

	def set_type(self):
		"Is it a full experiment or just a preexperiment"
		POWDER = re.compile(r"""(?P<name>powder|\S+?)[\-_]?(Mon|Tue|Wed|Thu|Fri|Sat|Sun)- 
										(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)- 
										\d\d-\d\d-\d\d-\d\d-\d\d\d\d""",re.VERBOSE)
		if POWDER.match(self.name):
			return 'powder'
		if 'pre_datacoll' in self.ini_types and 'datacoll' in self.ini_types: 
			return 'full'
		elif 'pre_datacoll' in self.ini_types and  not 'datacoll' in self.ini_types: 
			return 'pre'
		if 'datacoll' in self.ini_types and  not 'pre_datacoll' in self.ini_types: 
			return 'full_no_pre'
		else:
			return 'other'
	
	def notes(self):
		"""Notes about the dataset"""
		pre_path = os.path.join(self.d,'pre_'+self.name+'_notes.txt')
		notes_path = os.path.join(self.d,self.name+'_notes.txt')
		notes = ''
		if os.path.exists(pre_path):
			notes += open(pre_path,'r').read()
		elif os.path.exists(notes_path):
			notes += open(notes_path,'r').read()
		return notes

class IniFile:
	"""Class used to proccess various types of ini files.
	It uses a built-in ConfigParser module for parsing ini config files
	"""

	def __init__(self,file):
		self.file = file
		self.type = self.type()

	def exists(self):
		return os.path.exists(self.file)

	def type(self):
		"""Determine which type of ini file we have"""
		INI_NAME = re.compile(r'(?P<pre>pre)?_?(?P<name>[ .\,()\!\+\-\w]+)_(?P<type>\w+).ini')
		match = INI_NAME.match(os.path.basename(self.file))
		if match:
			t = '%(pre)s_%(type)s' % match.groupdict()
			return t.replace('None_','')
		else:
			return 'crysexpset'

	def parser(self):
		p = ConfigParser.ConfigParser()
		p.read(self.file)
		return p

	def sections(self):
		p = self.parser()
		return p.sections()

	def as_dictionary(self):
		p = self.parser()
		return dict([(sec,p.items(sec)) for sec in p.sections()])

class DatFile:
	"""Class used to proccess various dat files.
	"""

	def __init__(self,file):
		self.file = file
		self.type = self.type()

	def exists(self):
		return os.path.exists(self.file)

	def type(self):
		"""Determine which type of ini file we have"""
		DAT_NAME = re.compile(r'(?P<name>[ .\,()\!\+\-\w]+)_(?P<type>\w+).dat')
		match = DAT_NAME.match(os.path.basename(self.file))
		if match:
			t = '%(type)s' % match.groupdict()
			return t
	
	def json(self):
		from math import sin, pi
		def resolution(theta):
			theta = float(theta)
			LAMBDA = 1.54128
			return str(LAMBDA/(2*sin(theta*pi/360.)))
		lines = open(self.file,'r').readlines()
		lines = lines[2:]
		length = len(lines[0].split())
		out = [[] for i in range(length)]
		for line in lines:
			tmp = line.split()
			for i in range(length):
				out[i].append(tmp[i])
		#thetas = map(resolution,out[0])
		out1 =	map(list,zip(out[0],out[1]))
		out2 =	map(list,zip(out[0],out[2]))
		return {'out1':out1, 'out2':out2}

class Syncronize:
	"""
	This class syncronizes the directory where the copy of the
	data is stored on the local machine (LOCAL) 
	with the remote directory on the diffractometer (REMOTE_MNT)
	"""
	def __init__(self,refresh=False):
		if not refresh:
			self.remote_dirs = pickle.load(open('remote.pkl','r'))
			self.local_dirs = pickle.load(open('local.pkl','r'))
		else:
			self.set_dirs()

	def is_dataset(self,dirs):
		return 'frames' in dirs and 'log' in dirs

	def check_new_on_remote(self):
		top = REMOTE_MNT
		l = self.remote_dirs
		new = []
		for (d, dirs, files) in os.walk(top):
			if self.is_dataset(dirs) and not d in l:
				print d
				new.append(d)
		self.remote_dirs += new	
		pickle.dump(self.remote_dirs,open('remote.pkl','w'))
		return new

	def set_dirs(self):
		for top in (LOCAL,REMOTE_MNT):
			l = []
			for (d, dirs, files) in os.walk(top):
				if self.is_dataset(dirs):
					l.append(d)
			if top == REMOTE_MNT: 
				pickle.dump(l,open('remote.pkl','w'))
				self.remote_dirs = l
			if top == LOCAL: 
				pickle.dump(l,open('local.pkl','w'))
				self.local_dirs = l
	
	def sorted_by_mtimes(self):
		return sorted(self.remote_dirs,key=os.path.getmtime)

	def populate_database_with_new(self):
		print '%d experiments in the database' % Experiment.objects.count()
		dirs = self.check_new_on_remote()
		for d in dirs:
			ds = Dataset(d)
			try:
				exp = self.exp_from_dataset(ds)
				exp.save()
				print 'Saved %s' %exp.name
			except:
				exp = self.exp_from_dataset(ds)
				print 'Made %s but could not save it!' %exp.name
	
	def populate_database(self):
		print '%d experiments in the database' % Experiment.objects.count()
		dirs = self.remote_dirs
		#dirs = self.local_dirs
		for d in dirs:
			ds = Dataset(d)
			exp = self.exp_from_dataset(ds)
			try:
				exp.save()
				print 'Saved %s' %exp.name
			except:
				print 'Made %s but could not save it!' %exp.name

	def exp_from_dataset(self,ds):
		"""Make a new Experiment from Dataset class
		in crysalis application"""
		exp = Experiment()
		exp.name 		= ds.name
		exp.origdir		= ds.d
		exp.type		= ds.type
		exp.start 		= ds.get_datetime('start time') 
		exp.end			= ds.get_datetime('any end time') 
		exp.a, exp.b, exp.c, exp.alpha, exp.beta, exp.gamma, exp.volumen = ds.get_cell()
		exp.sg			= ds.get_space_group() 
	
		exp.notes		= ds.notes()
		exp.comment		= ds.get_comment()
		if ds.get_user():
			exp.user, created	= User.objects.get_or_create(username=ds.get_user())
		return exp

class MovieMaker:
	"""Makes animated gifs for crystal rotation 
	and flash files from diffraction images"""

	def __init__(self,experiment):
		self.exp = experiment

	def examine_imgs(self):
		"""Testing of possible types of datasets"""
		ds = Dataset(self.exp.origdir)
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

	def copy_crystal_jpg(self):
		"""Copy one crystal photo to media subdirectory"""
		movie_dir = os.path.join(EXPERIMENTS_DIR,str(self.exp.id))
		jpgs = glob.glob(self.exp.origdir+'/movie/*.jpg')
		if not os.path.exists(movie_dir):
			os.mkdir(movie_dir)
		if not jpgs:
			print 'No jpgs for %s' %self.exp
		try:
			shutil.copy(choice(jpgs),movie_dir+'/crystal.jpg')
		except:
			print 'Copy crystal photo failed!'

	def make_animated_image(self):
		"""
		Makes an animated gif from a series of crystal photos
		stored in the 'movie' subdirectory. The only problem
		is the bad naming of the jpgs so that they have to be renamed 
		before using convert comand in order to make smooth rotation.
		"""
		media = os.path.join(EXPERIMENTS_DIR,str(self.exp.id))
		if not os.path.exists(media):
			os.makedirs(media)
		gif = os.path.join(media,'animated.gif')
		jpgs = glob.glob(self.exp.origdir+'/movie/*.jpg')
		if os.path.exists(gif):
			print 'animated.gif exists for %s' %self.exp
		if jpgs:
			for jpg in jpgs:
				shutil.copy(jpg,TMPDIR)
			try:
				jpgs = glob.glob(os.path.join(TMPDIR,'*.jpg'))
				common = os.path.commonprefix(jpgs)
				name_regex = re.compile(r'%s(?P<number>\d+).jpg'%common)
				for jpg in jpgs:
					match = name_regex.match(jpg)
					new_name = common + '_%03d' % int(match.groups()[0]) + '.jpg'
					os.rename(jpg,new_name)
				jpgs = glob.glob(os.path.join(TMPDIR,'*.jpg'))
				for jpg in jpgs:
					command = 'convert -draw \'stroke black line 384,270,384,306\' -draw \'stroke black line 364,288,404,288\' %s %s' %(jpg,jpg)
					os.system(command)
				os.chdir(TMPDIR)
				os.system('convert -resize 30% -delay 15 -loop 0 *.jpg animated.gif')
				shutil.copy('%s/%s' %(TMPDIR,'animated.gif'),media)
				print 'Copied %s/%s to %s' %(TMPDIR,'animated.gif',media)
			except:
				print 'For some reason could not make animated.gif for %s' %self.exp.name
			for f in os.listdir(TMPDIR): 
				os.remove(os.path.join(TMPDIR,f))

	def movie_from_frames(self,diff2jpeg=True,convert=True):
		"""
		Makes a flash movie from diffraction frames
		"""
		runs = []
		frames_dir = os.path.join(self.exp.origdir,'frames')
		if os.listdir(frames_dir) == []:
			print 'No frames for %s' %self.exp
			return
		frames = os.path.join(EXPERIMENTS_DIR,str(self.exp.id),'frames')
		if not os.path.exists(frames):
			os.mkdir(frames)

		#Uses diff2jpeg to make jpegs from images
		imgs = glob.glob('%s/*.img'%frames_dir)
		if diff2jpeg:
			for img in imgs:
				os.system('diff2jpeg %s' %img)
				print 'diff2jpeg %s' %img

		patt = re.compile(r'(?P<pre>pre_)?(?P<name>[ \,\w\-\+\!]+)(?<!ref_\d_\d)_(?P<run>\d+)_(?P<image>\d+).jpg')
		jpgs = map(os.path.basename,glob.glob('%s/*.jpg'%frames_dir))
		for jpg in jpgs:
			match = patt.match(jpg)
			if match:
				os.system('mv %s %s'%(os.path.join(frames_dir,jpg),frames))
				grps = match.groupdict()
				new = '%s/%s_%03d_%03d.jpg' % (frames,grps['name'],int(grps['run']),int(grps['image']))
				jpg = os.path.join(frames,jpg)
				if grps['run'] not in runs: 
					runs.append(grps['run'])
				command = 'convert 	-resize 30%% -gravity NorthEast -fill \'#33f\' -pointsize 18 -annotate +5+5 \'run: %s frame: %s\'  %s %s' %(grps['run'],grps['image'],jpg,new)
				if convert:
					os.system(command)
				print command
		# Make a flash movie file
		print 'Making flash movies from frames'
		for run in runs:
			print 'jpeg2swf -r 5 %s/%s_%03d_*.jpg -o %s/run%03d.swf' %(frames,grps['name'],int(run),frames,int(run))
			os.system('jpeg2swf -r 5 %s/%s_%03d_*.jpg -o %s/run%03d.swf' %(frames,grps['name'],int(run),frames,int(run)))
		# Clean all jpg files from both directories
		print 'Cleaning %s' %frames_dir
		os.system('rm %s/*.jpg' %frames_dir)
		print 'Cleaning %s' %frames
		os.system('rm %s/*.jpg' %frames)

if __name__ == '__main__':
	s = Syncronize(refresh=True)
	s.populate_database()
