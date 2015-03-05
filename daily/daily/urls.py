from django.conf.urls import patterns, include, url
from access.views import indexView,searchView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'daily.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^search/$',searchView.as_view()),
    url(r'^daily/index/$',indexView.as_view()),
    #url(r'^readAccess/$','access.views.handle_log'),
    url(r'^admin/', include(admin.site.urls)),
)
