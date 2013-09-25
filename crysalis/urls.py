from django.conf.urls.defaults import *
from homebase.crysalis.views import *

urlpatterns = patterns('',
     (r'^create_pdf/$',create_pdf),
     (r'^historylog/$',historylog),
     (r'^ccdlogs/$',ccdlogs),
     (r'^datasets/(?P<name>.+)?',dataset_list),
     (r'^duplicates/',duplicates),
     (r'^current/$',current),
     (r'^ccdlogs/(?P<log>crysalispro_ccdLOG.+)$',viewlog),
)
