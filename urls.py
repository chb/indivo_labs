from django.conf.urls.defaults import *
from views import *
import settings

# all this is under apps/labs
urlpatterns = patterns('',
    # authentication
    (r'^start_auth', start_auth),
    (r'^after_auth', after_auth),
    (r'^lab$', list_labs), # can't use "list" obviously
    # (r'^labs/new$', new_med),
    # (r'^labs/(?P<med_id>[^/]+)', one_med),
    # (r'^$', lambda request: index()),
    (r'^jmvc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.JMVC_HOME}),
    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.JS_HOME})
)


