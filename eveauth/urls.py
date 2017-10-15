from django.conf.urls import url
from django.contrib.auth.views import logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^logout/$', logout, {'next_page': "/"}, name="logout"),
    url(r'^services/$', views.services, name="services"),
    url(r'^toggle_theme/$', views.toggle_theme, name="toggle_theme"),
    url(r'^services/mumble/update_password/$', views.update_mumble_password, name="update_mumble_password"),
    url(r'^services/forum/update_password/$', views.update_forum_password, name="update_forum_password"),
    url(r'^templinks/$', views.templink_index, name="templink_index"),
    url(r'^templinks/create/$', views.templink_create, name="templink_create"),
    url(r'^templinks/submit/$', views.templink_submit, name="templink_submit"),
    url(r'^templinks/disable/([0-9]+)$', views.templink_disable, name="templink_disable"),
    url(r'^templinks/([0-9A-Za-z]+)/$', views.templink_landing, name="templink_landing"),
    url(r'^templinks/([0-9A-Za-z]+)/submit$', views.templink_landing_submit, name="templink_landing_submit"),
    url(r'^users/([0-9]+)$', views.registeredusers_index, name="registeredusers_index"),
    url(r'^user/([0-9]+)$', views.view_user, name="view_user"),
    url(r'^user/([0-9]+)/updategroups$', views.user_updategroups, name="user_updategroups"),
    url(r'^user/all/updategroups$', views.user_updategroups_all, name="user_updategroups_all"),
    url(r'^groupadmin/$', views.groupadmin_index, name="groupadmin_index"),
    url(r'^groupadmin/create$', views.groupadmin_create, name="groupadmin_create"),
    url(r'^groupadmin/([0-9]+)/$', views.groupadmin_edit, name="groupadmin_edit"),
    url(r'^groupadmin/([0-9]+)/delete$', views.groupadmin_delete, name="groupadmin_delete"),
    url(r'^groupadmin/([0-9]+)/kick/([0-9]+)$', views.groupadmin_kick, name="groupadmin_kick"),
    url(r'^mumble/$', views.mumbleadmin_index, name="mumbleadmin_index"),
    url(r'^mumble/kick/([0-9]+)$', views.mumbleadmin_kick, name="mumbleadmin_kick"),
]
