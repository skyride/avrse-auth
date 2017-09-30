from django.conf.urls import url
from django.contrib.auth.views import logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^logout/$', logout, {'next_page': "/"}, name="logout"),
    url(r'^services/$', views.services, name="services"),
    url(r'^services/update_password/$', views.update_mumble_password, name="update_mumble_password"),
]
