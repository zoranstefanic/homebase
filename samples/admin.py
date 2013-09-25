from homebase.samples.models import *
from django.contrib import admin

class SampleAdmin(admin.ModelAdmin):
	pass

admin.site.register(Sample,SampleAdmin)
