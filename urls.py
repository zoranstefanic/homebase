from django.conf.urls.defaults import *
from django.conf import settings
from homebase.settings import SAMPLES_DIR
from profiles.forms import ProfileForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# This is a toy application for choosing color schemes
	(r'^colors/', include('homebase.colors.urls')),
	
	# Main applications
    (r'^experiments/', include('homebase.experiments.urls')),
    (r'^samples/', include('homebase.samples.urls')),
    (r'^crysalis/', include('homebase.crysalis.urls')),
    (r'^schedule/', include('homebase.schedule.urls')),
	
	# Static media  
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^srv/xcalibur_homebase/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': SAMPLES_DIR, 'show_indexes': True}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Auth
    #(r'^login/','django.contrib.auth.views.login'),
    #(r'^logout/','django.contrib.auth.views.logout'),

	# django profiles
    ('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
	(r'^profiles/', include('profiles.urls')),

	(r'^accounts/', include('registration.backends.default.urls')),
    
	# Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
	
	# Homepage
    (r'^$', 'homebase.experiments.views.homepage'),
)
