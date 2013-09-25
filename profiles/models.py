from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        profile = Profile(user=user)
        profile.save()


class Profile(models.Model):
	"""
	The model describing the person requesting 
	an X-ray analysis of the sample.
	"""
	user			= models.ForeignKey(User, unique=True)
	address			= models.TextField(help_text='Address of the person ordering X-ray analysis',default='Bijenicka 54\nP.O. Box 180\n10000 Zagreb')
	telephone		= models.CharField(null=True,blank=True,max_length=50,default='+385 1 ???????')
	lab				= models.TextField(help_text='Lab or department of the person ordering X-ray analysis', default='LCBC')
	institution		= models.TextField(help_text='Institution',default='Rudjer Boskovic Institute')
	account_number	= models.CharField(help_text='Account number', max_length=30)

	def __unicode__(self):
		return '%s - %s' %(self.user.username,self.institution)

	def is_operator(self):
		"Returns True if user is a member of 'operators' group"
		g = Group.objects.get(name='operators')
		return g in self.user.groups.all()

post_save.connect(create_profile, sender=User, dispatch_uid="user-profile-signal")
