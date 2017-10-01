from django.conf.urls import url
from django.contrib.auth.views import logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^logout/$', logout, {'next_page': "/"}, name="logout"),
    url(r'^services/$', views.services, name="services"),
    url(r'^services/update_password/$', views.update_mumble_password, name="update_mumble_password"),
    url(r'^templinks/$', views.templink_index, name="templink_index"),
    url(r'^templinks/create/$', views.templink_create, name="templink_create"),
    url(r'^templinks/submit/$', views.templink_submit, name="templink_submit"),
    url(r'^templinks/disable/([0-9]+)$', views.templink_disable, name="templink_disable")
]
