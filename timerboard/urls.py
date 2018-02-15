from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^delete/([0-9]+)$', views.delete, name="delete")
]
