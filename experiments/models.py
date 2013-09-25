import os,glob
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from homebase.samples.models import Sample
from homebase.settings import PROJECT_DIR

class Experiment(models.Model):
	"""The main model describing one particular experiment """
	name			= models.CharField(max_length=50)
	origdir			= models.CharField('Directory', help_text='Directory with files on local machine',max_length=300)
	type			= models.CharField(max_length=10)
	start 			= models.DateTimeField(help_text='Start of experiment')
	end				= models.DateTimeField(help_text='End of experiment',null=True)
	errors			= models.TextField(help_text='Possible errors',max_length=200,null=True)
	notes			= models.TextField(help_text='Notes on experiment',max_length=500,null=True)
	comment			= models.TextField(help_text='User comment',max_length=500,null=True)

	a		  		= models.DecimalField('Cell length a',max_digits=6, decimal_places=3, null = True)
	b				= models.DecimalField('Cell length b',max_digits=6, decimal_places=3, null = True)
	c				= models.DecimalField('Cell length c',max_digits=6, decimal_places=3, null = True)
	alpha			= models.DecimalField('Cell angle alpha',max_digits=6, decimal_places=3, null = True)
	beta			= models.DecimalField('Cell angle beta',max_digits=6, decimal_places=3, null = True)
	gamma			= models.DecimalField('Cell angle gamma',max_digits=6, decimal_places=3, null = True)
	volumen			= models.FloatField('Volumen',null=True)
	sg				= models.CharField('Space group',max_length=10,null=True)
	
	# Foreign keys
	sample			= models.ForeignKey(Sample,help_text='Sample on which experiment is taken', null=True)
	user			= models.ForeignKey(User,help_text='User which has performed this experiment', null=True)
	
	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return '/experiments/%s' %self.id

	def img_url(self):
		return '/media/experiments/%s/crystal.jpg' %self.id
	
	def frames_url(self):
		return '/media/experiments/%s/frames/' %self.id

	def has_movies(self):
		"""Wheather there are any movies in frames directory"""
		swf = os.path.join(PROJECT_DIR,self.frames_url()[1:],'*.swf')
		if glob.glob(swf):
			return True
		return False

	def duration(self):
		"The duration of the experiment"
		delta = self.end - self.start
		days = delta.days
		hours = delta.seconds/3600.
		minutes = (hours - int(hours))*60
		return (days,int(hours),int(minutes))

