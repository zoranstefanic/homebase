import glob
import re
import os
import subprocess
from time import sleep
from datetime import datetime
from paths import *
from django.db import models
from homebase.settings import PROJECT_DIR

DATE_TIME = '(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d\d \d\d:\d\d:\d\d \d\d\d\d'
TIMEFMT = '%a %b %d %H:%M:%S %Y'
LOGTIMEFMT = '%a-%b-%d-%H-%M-%S-%Y'

regex = {
	#		'LOGSTRT':		re.compile(r"CCD HISTORY LOG started at (?P<time>%s)" %DATE_TIME),
			'DCPREINFO':	re.compile(r"DC PRE INFO: Experiment C:(?P<folder>.+)?\\pre_(?P<name>.+)\.run" ),
			'RUNLIST':		re.compile(r"Run list: (?P<folder>.+)\\(?P<pre>pre_)?(?P<name>.+)\r" ),
			'DCSTRT':		re.compile(r"DC (?P<sr>[SR]) \"(?P<folder>.+)\\(?P<pre>pre_)?(?P<name>.+)\"" ),
			'CALIBR':		re.compile(r"CALIBRATION EXPERIMENT INFO: Starting Cu experiment at (?P<distance>\d+\.\d+)mm \((?P<time>%s)\)" %DATE_TIME ),
			'POWDER':		re.compile(r"(---------- )?POWDER EXPERIMENT INFO: Started at (?P<time>%s)" %DATE_TIME),
			'TIME':			re.compile(r"DC (?P<sr>[SR]) command at (?P<time>%s)" %DATE_TIME),
			'USRSTOP':		re.compile(r"User stop at (?P<time>%s)" %DATE_TIME),
			'FINISH':		re.compile(r"Data collection successfully finished at (?P<time>%s)" %DATE_TIME),
			'RUN':			re.compile(r"Run (?P<run_num>\d+) started at (?P<start>%s)" %DATE_TIME),
			'UBFIT':		re.compile(r"UB fit with (?P<obs>\d+) obs out of (?P<total1>\d+) \(total:(?P<total2>\d+),skipped:(?P<skipped>\d+)\) \((?P<percent>\d\d\.\d\d)\%\)"),
			'OPSCAN':		re.compile(r'(?P<omphi>(Omega|Phi)) scan:\s*(?P<om1>-?\d+\.\d+) to \s*(?P<om2>-?\d+\.\d+) \(\s+(?P<num>\d+) frames,\s*(?P<exp>\d+\.\d+)s\) at [to]:\s*(?P<to>-?\d+\.\d+),[kt]:\s*(?P<kt>-?\d+\.\d+),[pk]:\s*(?P<pk>-?\d+\.\d+),dd:\s+(?P<dd>\d+\.\d+)'),
			'FOLDER':		re.compile(r"Frames folder: (?P<folder>.+?)\\frames"),
			'EFTIME':		re.compile(r"EXPECTED FINISH TIME:\s+\((?P<done>\d+),(?P<total>\d+),end:(?P<etime>%s)\)( \[\+\/\- (?P<plus_minus>\d+)m \])?" %DATE_TIME),
			'REMEAS':		re.compile(r'Warning: Frame (?P<frame>\d+) of run (?P<run_num>\d+) remeasured with exposure time\s+(?P<exposure>\d+\.\d+)s due to overflow!'),
			'OVERFL':		re.compile(r'Warning: Frame (?P<frame>\d+) of run (?P<run_num>\d+) contains (?P<overflow>overflows)'),
			'DELETE':		re.compile(r'DELETE INFO( \(RECYCLING BIN\))?: Deleting files in frames directory\.\.\. \((?P<folder>.+)?\\frames\\\*\.\*\)'),
			'CLEAR':		re.compile(r'DC PRE ACTION: Button clear path\r'),
			}

class LogDir(models.Model):
	"""
	Django model class that represents log directory where 
	the files change.
	"""
	directory 	= models.CharField('Log directory',primary_key=True, help_text='Full path to the log dir',max_length=300)
	modified	= models.DateTimeField(help_text='Log directory last modified time')
	checked		= models.DateTimeField(help_text='When was log dir last checked')
	numlogs		= models.IntegerField(help_text='Number of ccd log files in log directory')
	
	def __unicode__(self):
		return "%s" %self.directory
	
	def update(self):
		"""
		Sets a list of log files sorted by time in the log name
		then the times dir was modified and the last check time
		"""
		self.directory = LOG_FILE_DIR
		self.patt = re.compile(r"crysalispro_ccdLOG(?P<date>[-\w]+).txt")
		self.logs = self.get_logs()
		self.last = self.logs[-1]
		self.numlogs = len(self.logs)
		self.checked = datetime.now()
		mtime = os.path.getmtime(self.directory)
		self.modified = datetime.fromtimestamp(mtime)
		self.save()

	def check(self):
		"""
		Checks wheather any new ccd log files appeared
		"""
		self.checked = datetime.now()
		mtime = os.path.getmtime(self.directory)
		self.modified = datetime.fromtimestamp(mtime)
		if len(self.get_logs())>self.numlogs:
			self.numlogs = len(self.logs)
			return True
		return False

	def create_logfiles(self):
		"""
		Goes through the list of log files and creates new ones
		if not existing
			"""
		for f in self.logs:
			try:
				lf = LogFile.objects.get(name=f)
			except:
				lf = LogFile()
				lf.create(f)
				#lf.create_datasets()

	def watch(self,time=10):
		"""
		Watches the log directory for newly created log files
		"""
		while True:
			if self.check():
				print 'Number of logs changed to %d' % self.numlogs 
			else:
				print 'Number of logs the same = %d' % self.numlogs 
				sleep(time)

	def get_logs(self):
		"Returns unordered list of ccd log files"
		files =	map(os.path.basename,glob.glob(self.directory + '/*.txt'))
		logs = [f for f in files if self.patt.match(f)]
		logs_times = []
		for f in logs:
			d = self.patt.match(f).groups()[0]
			t = datetime.strptime(d,LOGTIMEFMT)
			logs_times.append((f,t))
		sorted_logs = sorted(logs_times,key=lambda a: a[-1])
		return [l[0] for l in sorted_logs]

	def concatenate_logs(self):
		"Makes one big chronological log file"
		out = open('concatenate.logs','w')
		for f in self.logs:
			lines = open(os.path.join(self.directory,f),'r').readlines()
			out.writelines(lines)
		out.close()

class LogFile(models.Model):
	"""
	"""
	name		= models.CharField('Log file name',primary_key=True, max_length=50)
	date		= models.DateTimeField(help_text='Log open date')
	last		= models.BooleanField(help_text='Is this the last ccd?',default=False)
	logdir		= models.ForeignKey('LogDir')
	
	def __unicode__(self):
		return "%s" %self.name

	def create(self,file):
		self.name = file
		self.patt = re.compile(r"crysalispro_ccdLOG(?P<date>[-\w]+).txt")
		self.fullpath = os.path.join(LOG_FILE_DIR,self.name)
		self.logdir = LogDir.objects.get(directory=LOG_FILE_DIR)
		self.set_date()
		self.fh = open(self.fullpath,'r')
		self.lines = []
		self.ln = 0  # Current line number
		self.patterns = regex
		self.current = None
		# self.datasets = LogDataset.objects.none()
		self.datasets = []	
		self.interval = 20 # sleep interval	
		self.save()

	def create_datasets(self):
			while True:
				line = self.nextline()
				if line:
					if self.matches(line,'DCSTRT','POWDER','CALIBR'):	
						if self.current:							
							self.current.update(line)						
							try:
								self.current.save()						
							except:
								print 'Could not save at %s' %line
							self.current = LogDataset()
							self.current.create(line,self)						
						if not self.current:							
							self.current = LogDataset()
							self.current.create(line,self)						
							self.current.update(line)						
					elif self.matches(line,'USRSTOP','FINISH'):			
						if self.current:							
							self.current.update(line)						
							try:
								self.current.save()						
							except:
								print 'Could not save at %s' %line
							self.datasets.append(self.current)
						if not self.current:							
							print 'None stopped at %s' % line
						self.current = None						
					else:												
						if self.current:							
							self.current.update(line)				
						if not self.current:							
							pass
				else:
					if self.current:
						print 'Log closed with dataset on'
						try:
							self.current.save()						
						except:
							print 'Could not save at %s' %line
					break

	def watch1(self):
		while True:
			line = self.nextline()
			if line:
				print line.strip()
			else:
				return
				print self.ln
				sleep(self.interval)

	def set_date(self):
		d = self.patt.match(self.name).groups()[0]
		self.date = datetime.strptime(d,LOGTIMEFMT)

	def get_absolute_url(self):
		return '/crysalis/ccdlogs/%s' %self.name
	
	def nextline(self):
		line = self.fh.readline()
		if line:
			self.ln += 1
			self.lines.append(line)
			return line
		return 

	def unique_datasets(self):
		"""Goes through all datasets in a log file and keeps only the 
		last one based on equality of datasets
		(namely that the ds.folder is the same)"""
		self.datasets.reverse()
		unique = []
		for ds in self.datasets:
			if not ds in unique:
				unique.append(ds)
		self.datasets.reverse()
		return unique
				
	def rsync_all(self,rsync=True):
		for ds in self.unique_datasets():
			if ds.local_dir_exists():
				print 'Local exists: %s' %ds.local
			else:
				if ds.remote_dir_exists():
					print 'rsync -avzu %s/ %s' %(ds.remote, ds.local)
					if rsync:
						print 'rsync -avzu %s %s' %(ds.remote, ds.local)
						#subprocess.call(['rsync', '-avzu', ds.remote + '/', ds.local])
				else:
					print 'Remote not there: %s' %ds.remote

	def matches(self,line,*patt):
		"Returns true if line matches any of the 'self.patterns'"
		patterns = [self.patterns[what] for what in patt]
		if not patt:
			patterns = self.patterns.values()
		for patt in patterns:
			if patt.match(line):
				return True 
		return False

	def get_lines_pattern(self,*patt):
		"""Get only lines that match pattern
		If no pattern specified than lines matching anything in 
		self.patterns are appended."""
		return [line for line in self.lines if self.matches(line,*patt)]

	def line_dict(self,line,patt):
		return self.patterns[patt].match(line).groupdict()
		
	def as_pre(self,num=None):
		"Represent the whole file as string with colored lines that match"
		if num: num = -num 
		s = ''
		ln = 1
		for line in self.lines[num:]:
			#line = "<span id='%r'> %r  " %(ln,ln) + "</span>" + line.strip('\r\n') 
			line = line.strip('\r\n') 
			if self.matches(line):
				s += '<span class="colored">' + line + '</span>' + '\n'
			else:
				s += line + '\n'
			ln += 1
		return s

	def dcinfo(self):
		"Extract data collection information from log file"
		s = '%-30s %5s %5s %5s\n' % ('name', 'pre', 'remote', 'local')
		for ds in reversed(self.datasets):
			s += '%-30s %5s %5s %5s :  %10s %10s\n' % (ds.name, ds.pre, ds.remote_dir_exists(), ds.local_dir_exists(), ds.ended, (ds.finish - ds.start))
		return s

class LogDataset(models.Model):
	"""The main model describing one particular experiment """
	name			= models.CharField(max_length=50)
	folder			= models.CharField('Original folder', help_text='Directory where original files are collected',max_length=300, null=True)
	local			= models.CharField('Local folder', help_text='Directory where files are rsynced',max_length=300,null=True)
	remote			= models.CharField('Mount of original dir', help_text='Mount of remote dir localy',max_length=300)
	type			= models.CharField(max_length=10)
	pre				= models.CharField(max_length=10)
	ended			= models.CharField(max_length=10)
	startline 		= models.IntegerField(help_text='Starting line') 
	start 			= models.DateTimeField(help_text='Start of experiment',primary_key=True)
	finish			= models.DateTimeField(help_text='End of experiment',null=True)
	#lines			= models.TextField(help_text='Lines')
	log			= models.ForeignKey(LogFile,help_text='CCD log file that logs experiment', null=True)

	def create(self, line, log):
		self.patterns = log.patterns
		self.log = log
		self.lines = [line]
		self.startline = log.ln
		self.pre = self.is_pre(line)
		self.set_type(line)
		self.data = {}

	def update(self,line):
		self.lines.append(line)
		for name,patt in self.patterns.items():
			if patt.match(line):
				gd = patt.match(line).groupdict()	
				self.data.setdefault(name,[]).append(gd)
		self.get_sr()
		self.get_folder()
		self.get_name()
		self.start = self.get_start()
		self.finish	= self.get_finish()
		return

	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return '/crysalis/datasets/%s' %self.name

	def __repr__(self):
		if self.valid():
			return '%5s %-30s %s' %(self.pre, self.name, self.start)
		else:
			return '!!! %-30s %s' %(self.name, self.start)

	def __eq__(self,other):
		try:
			return self.folder == other.folder
		except:
			return True

	def debug(self):
		valid = 'vi +%d %s\n' %(self.startline,self.log.name)
		invalid = ''
		keys = ['data', 'ended', 'finish', 'folder', 'lines', 'local', 'log', 'name', 'patterns', 'pre', 'remote', 'start', 'start_restart', 'startline', 'type']
		for a in keys:
			try:
				valid += '%20s = %s\n' %(a,self.__getattribute__(a))
			except:
				invalid += 'xxxx %15s\n' %a
		return 'VALID:\n %s\n INVALID:\n %s\n' %(valid,invalid)

	def valid(self):
		keys = ['data', 'ended', 'finish', 'folder', 'lines', 'local', 'log', 'name', 'patterns', 'pre', 'remote', 'start', 'start_restart', 'startline', 'type']
		for a in keys:
			try:
				self.__getattribute__(a)
			except:
				return False
		if self.start == None or self.ended == None:
			return False
		return True

	def set_type(self,line):
		if self.patterns['DCSTRT'].match(line):
			self.type = 'normal'
		if self.patterns['POWDER'].match(line):
			self.type = 'powder'
		if self.patterns['CALIBR'].match(line):
			self.type = 'calibr'

	def get_sr(self):
		try:
			self.start_restart = self.data['TIME'][0]['sr']
		except:
			self.start_restart = None
	
	def get_folder(self):
		try:
			if self.data.has_key('FOLDER'):
				self.folder = self.data['FOLDER'][0]['folder']
			else:
				self.folder = self.data['DCSTRT'][0]['folder']
			self.local = win_to_local(self.folder)
			self.remote = win_to_remote_mnt(self.folder)
		except:
			self.folder = None

	def get_name(self):
		try:
			if self.data.has_key('RUNLIST'):
				self.name = self.data['RUNLIST'][0]['name']
			elif self.data.has_key('DCSTRT'):
				self.name = self.data['DCSTRT'][0]['name']
		except:
			self.name = None

	def get_start(self):
		try:
			return self.as_datetime(self.data['TIME'][0]['time'])
		except:
			return None

	def get_finish(self):
		if 'USRSTOP' in self.data.keys():
			self.ended = 'userstop'
			return self.as_datetime(self.data['USRSTOP'][0]['time'])
		elif 'FINISH' in self.data.keys():
			self.ended = 'success'
			return self.as_datetime(self.data['FINISH'][0]['time'])
		else:
			self.ended = None
			return None
	
	def as_datetime(self,s):
		return datetime.strptime(s,TIMEFMT)

	def local_dir_exists(self):
		return os.path.exists(self.local)

	def remote_dir_exists(self):
		return os.path.exists(self.remote)

	def rsync_to_current(self):
		where = os.path.join(LOCAL,'current')	
		if not os.path.exists(where):
			os.mkdir(where)
		print 'rsync -av --exclude=tmp/ %s %s' %(self.remote + '/', where)
		#subprocess.call(['rsync', '-avzun', '--exclude=tmp/',self.remote + '/', self.local])
	
	def is_pre(self,line):
		'Is it a preexperiment?'
		if self.patterns['POWDER'].match(line) or self.patterns['CALIBR'].match(line):
			return False
		d = self.patterns['DCSTRT'].match(line).groupdict()
		return bool(d['pre'])

class HistoryLog:
	"""
	In directory /mnt/xcalibur_C/Xcalibur/CrysAlisINI there 
	is a file XcaliburHistory.log which acctually keeps the history of 
	the data collections being connducted.
	This is a good starting point of tracking the experiments.
	Unfortunatelly this only tracks from mid July 2009.
	Also the data collection experiment gets writen to this 
	file only after the finish of experiment
	"""
	def __init__(self):
		self.file = '/mnt/xcalibur/Xcalibur/CrysAlisINI/XcaliburHistory.log'
		self.ln = len(self.get_lines())
		self.linepattern = re.compile(r"Date: (?P<time>%s); source: Cu; total time:\s+(?P<sec>\d+) sec; exp name: (?P<folder>.+)?\\(?P<pre>pre_)?(?P<name>.+)\r" %DATE_TIME)
		self.dc = {}

	def get_lines(self):
		"Fill lines and number of lines"
		log = open(self.file,'r')
		self.lines = open(self.file,'r').readlines()
		log.close()
		return self.lines
		
	def print_lines(self):
		"""
		Main function that iterates over lines 
		"""
		for line in self.lines:
			m = self.linepattern.match(line)
			dic = m.groupdict()
			dic['local'] = win_to_local(dic['folder'])
			dic['remote_mnt'] = win_to_remote_mnt(dic['folder'])
			local_exists = os.path.exists(dic['local'])
			remote_exists = os.path.exists(dic['remote_mnt'])
			#print '%(pre)5s %(sec)10s %(folder)-50s %(local)-50s %(remote_mnt)s' % dic
			if not local_exists:
				if not remote_exists:
					#print '%(remote_mnt)-50s is gone' % dic
					pass
				else:
					print '%(remote_mnt)-50s ===== rsync =====> %(local)-50s' % dic
	
	def datacollections(self):
		"""
		Returns a list of tuples (time, folder) sorted by time
		"""
		l = []
		for line in self.lines:
			m = self.linepattern.match(line)
			d = m.groupdict()
			d['time'] = datetime.strptime(d['time'],TIMEFMT)
			l.append((d['time'],d['folder'],d['sec']))
			l = sorted(l,key=lambda a: a[0])
			l.reverse()
		return l

def test_all_datasets():
	success = []
	fail =	[]
	ld = LogDir()
	ld.update()
	for ccd in ld.logs:
		print ccd
		log = LogFile()
		log.create(ccd)
		log.create_datasets()
		datasets = log.unique_datasets()
		datasets.reverse()
		for ds in datasets:
			if ds.valid():
				success.append(ds)
			if not ds.valid():
				fail.append(ds)
	# group_datasets_by(success,'folder')
	# group_datasets_by(success,'name')
	return success, fail

if __name__ == '__main__':
	ld = LogDir()
	ld.watch_log_dir()
