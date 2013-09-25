from homebase.experiments.models import Experiment
from django.contrib import admin


class ExperimentAdmin(admin.ModelAdmin):
	pass
	#fields = ['name', 'start', 'end']
	list_display = ('name','start','notes')
	list_filter = ('user','start')

admin.site.register(Experiment,ExperimentAdmin)
