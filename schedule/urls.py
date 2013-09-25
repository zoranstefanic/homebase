from django.conf.urls.defaults import *
from homebase.experiments.views import *
from homebase.experiments.models import *
from homebase.schedule.views import *

info_dict = {
    'queryset' : Experiment.objects.all(),
    'date_field' : 'start',
}

urlpatterns = patterns('',
	(r'^calendar/(?P<year>\d{4})/$',calendar_year),
	(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/$',calendar_month),
	(r'^(?P<status>[FSX]?)$',schedule),
)

