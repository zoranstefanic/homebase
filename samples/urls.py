from django.conf.urls.defaults import *

from homebase.samples.views import *

urlpatterns = patterns('',
     (r'^new_small/$',new_small),
     (r'^new_protein/$',new_protein),
     (r'^delete_all_samples/$',delete_all_samples),
     (r'^$', samples_list),
     (r'(?P<sample_id>\d+)/$',view_sample),
     (r'(?P<sample_id>\d+)/edit/$',edit_sample),
     (r'(?P<sample_id>\d+)/delete/$',delete_sample),
     (r'added_by/(?P<name>\w+)/$',samples_added_by),
)
