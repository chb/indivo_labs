from django.conf.urls import patterns
from views import *
import settings
from django.conf import settings as rootsettings

# all this is under apps/labs
urlpatterns = patterns('',
    # authentication
    (r'^start_auth', start_auth),
    (r'^after_auth', after_auth),
    (r'^lab/(?P<lab_id>[^/]+)/$', show_lab),
    (r'^labs$', list_labs),
    # static
    ## WARNING NOT FOR PRODUCTION
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': rootsettings.SERVER_ROOT_DIR + settings.STATIC_HOME}),
    # (r'^labs/new$', new_med),
    # (r'^labs/(?P<med_id>[^/]+)', one_med),
    # (r'^$', lambda request: index()),
    (r'^jmvc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.JMVC_HOME}),
    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.JS_HOME})

)