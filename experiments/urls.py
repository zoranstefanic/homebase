from django.conf.urls.defaults import *
from homebase.experiments.views import *
from homebase.experiments.models import *

info_dict = {
    'queryset' : Experiment.objects.all(),
}

urlpatterns = patterns('',
	(r'^$',experiment_list),
	(r'^search/$',experiment_search),
	(r'^getip/$',getip),
	(r'^cells/$',cell_list),
	(r'^searchcells/$',experiment_search_cells),
	(r'^(?P<user>[a-zA-Z]+)/$',experiment_list),
	(r'^(?P<id>[\d]+)/$',view_experiment),
	(r'^(?P<id>[\d]+)/frames/$',experiment_frames),
	(r'^(?P<id>[\d]+)/stats/(?P<type>[a-z]+)/$',experiment_stats),
	(r'^(?P<id>[\d]+)/(?P<ini_type>[a-z]+)/$',experiment_ini),
	(r'^assignsample/(?P<id>[\d]+)/$',assignsample),
)
