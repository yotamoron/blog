from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blog.views.home', name='home'),
    # url(r'^blog/', include('blog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/', 'users.views.remember_me_login'),
    url(r'^accounts/', include('registration.urls')),
    url(r'^index/(?P<username>\w+)?(/?(?P<year>\d+)/(?P<month>\d+)?)?/?$',
            'main.views.index'),
    url(r'^view/(?P<post_id>\d+)/?$', 'main.views.view'),
    url(r'^delete/(?P<post_id>\d+)/?$', 'main.views.delete'),
    url(r'^post/(?P<post_id>\d+)?/?(?P<action>\w+)?/?$', 'main.views.post'),
    url(r'^search/$', 'main.views.search'),
    url(r'^tinymce/', include('tinymce.urls')),
)

