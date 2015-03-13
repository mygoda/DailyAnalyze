from django.conf.urls import patterns, include, url
from access.views import indexView,searchView,dataView
from django.contrib import admin
from django.conf import settings
import debug_toolbar
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'daily.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^search/$',searchView.as_view()),
    url(r'^index/$',indexView.as_view()),
    url(r'^destails/$',dataView.as_view()),
    #url(r'^readAccess/$','access.views.handle_log'),
    url(r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('',
    #(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT, 'show_indexes': True}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    (r'^debug/', include(debug_toolbar.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
