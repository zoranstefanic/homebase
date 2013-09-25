from django.db import models
from django.contrib.auth.models import User
from random import choice
import string
import datetime

SAMPLE_TYPES = (
    ('SM', 'small molecule'),
    ('PX', 'protein'),
)
SAMPLE_STATUSES = (
    ('S', 'scheduled'),
    ('F', 'finished'),
    ('X', 'on_xray'),
)
LT_CHOICES = (
    ('Yes', 'sample needs low temperature!'),
    ('No', 'not needed'),
    ('maybe', 'if available'),
)
ABSCONF_CHOICES = (
    ('no', 'not needed, no chiral atoms'),
    ('relative', 'at least one atom of known abs conf'),
    ('yes', 'yes determine abs conf!'),
)

def generate_code():
	"Generate 10 digit random string"
	return ''.join([choice(string.uppercase) for i in range(10)])

class Sample(models.Model):
	"""
	The main model describing one particular crystal sample.
	It can be either a SmallMolecule or Protein sample.
	This model only defines fields common to both.
	"""
	label		= models.CharField(help_text='The label of the sample',max_length=50)
	status		= models.CharField(help_text='Status of the sample',choices=SAMPLE_STATUSES,default='S',max_length=10)
	code		= models.CharField(help_text='Sample code used to connect to the experiment',default=generate_code,max_length=10)
	description	= models.TextField(help_text='Sample description',blank=True,null=True)
	date_added 	= models.DateTimeField(editable=False,auto_now_add=True)
	date_modified = models.DateTimeField(editable=False,auto_now=True)

	owner		= models.ForeignKey(User,null=True,blank=True,related_name='samples') 
	added_by	= models.ForeignKey(User,editable=False,related_name='added_samples') 

	def __unicode__(self):
		return self.label

class SmallMolecule(Sample):
	"""
	Subclass of Sample model describing small molecule samples. 
	"""
	type		= models.CharField(help_text='Small molecule or protein crystal?',choices=SAMPLE_TYPES,default='SM',editable=False,max_length=10)
	solvents	= models.TextField(help_text='Solvents used in crystallisation',blank=True,null=True)
	low_temp 	= models.CharField(help_text='Does it need low temperature?', choices=LT_CHOICES, default='No', max_length=5)
	abs_conf 	= models.CharField(help_text='Absolute configuration?', choices=ABSCONF_CHOICES, default='no', max_length=5)
	# Next fields are calculated by Marvin applet
	formula		= models.CharField(editable=False,max_length=100)
	mass 		= models.FloatField(editable=False,max_length=10)
	atomcount 	= models.FloatField(editable=False,max_length=10)
	marvin 		= models.TextField(editable=False)

	def __unicode__(self):
		return self.label

class Protein(Sample):
	"""
	Subclass of Sample model describing small protein samples. 
	"""
	type		= models.CharField(help_text='Small molecule or protein crystal?',choices=SAMPLE_TYPES,default='PX',editable=False,max_length=10)
	sequence	= models.TextField(help_text='Protein Sequence',blank=True, null=True, max_length=500)
	conditions 	= models.CharField(help_text='Crystallization conditions', null=True, blank=True, max_length=200)
	photo 		= models.ImageField(upload_to='sample_photos', null=True, blank=True)

	def __unicode__(self):
		return self.label
	
