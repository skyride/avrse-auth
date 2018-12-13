from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^update_password', views.UpdatePasswordView.as_view(), name="update_password")
]