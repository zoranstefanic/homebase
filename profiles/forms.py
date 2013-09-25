from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from profiles.models import *
 
class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		exclude = ('user',)
