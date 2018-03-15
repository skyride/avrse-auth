from django.conf.urls import url
from django.contrib.auth.views import logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^logout/$', logout, {'next_page': "/"}, name="logout"),
    url(r'^services/$', views.services, name="services"),

    url(r'^characters/$', views.characters_index, name="characters_index"),
    url(r'^characters/delete/([0-9]+)$', views.characters_delete, name="characters_delete"),
    url(r'^character/([0-9]+)$', views.characters_view, name="characters_view"),

    url(r'^groups/$', views.groups_index, name="groups_index"),
    url(r'^groups/([0-9]+)/leave$', views.groups_leave, name="groups_leave"),
    url(r'^groups/([0-9]+)/join$', views.groups_join, name="groups_join"),
    url(r'^groups/([0-9]+)/apply$', views.groups_apply, name="groups_apply"),

    url(r'^toggle_theme/$', views.toggle_theme, name="toggle_theme"),

    url(r'^services/mumble/update_password/$', views.update_mumble_password, name="update_mumble_password"),
    url(r'^services/forum/update_password/$', views.update_forum_password, name="update_forum_password"),

    url(r'^ships/$', views.assets_index, name="assets_index"),
    url(r'^ship/([0-9]+)$', views.assets_viewship, name="assets_viewship"),

    url(r'^admin/users/(?P<page>[0-9]+)/(?P<order_by>[a-zA-Z_]+)?$', views.registeredusers_index, name="registeredusers_index"),
    url(r'^admin/user/([0-9]+)$', views.view_user, name="view_user"),
    url(r'^admin/user/([0-9]+)/unlinkdiscord$', views.unlink_discord, name="unlink_discord"),
    url(r'^admin/user/([0-9]+)/updategroups$', views.user_updategroups, name="user_updategroups"),
    url(r'^admin/user/all/updategroups$', views.user_updategroups_all, name="user_updategroups_all"),

    url(r'admin/ships/([0-9]+)$', views.adminassets_index, name="adminassets_index"),
    url(r'admin/ship/([0-9]+)$', views.adminassets_viewship, name="adminassets_viewship"),

    url(r'^admin/characters/(?P<page>[0-9]+)/(?P<order_by>[a-zA-Z_]+)?$', views.characteradmin_index, name="characteradmin_index"),
    url(r'^admin/chararacter/([0-9]+)$', views.characteradmin_view, name="characteradmin_view"),

    url(r'^admin/groups/$', views.groupadmin_index, name="groupadmin_index"),
    url(r'^admin/groups/create$', views.groupadmin_create, name="groupadmin_create"),
    url(r'^admin/groups/([0-9]+)/$', views.groupadmin_edit, name="groupadmin_edit"),
    url(r'^admin/groups/([0-9]+)/delete$', views.groupadmin_delete, name="groupadmin_delete"),
    url(r'^admin/groups/([0-9]+)/kick/([0-9]+)$', views.groupadmin_kick, name="groupadmin_kick"),
    url(r'^admin/groups/app/([0-9]+)/([\w]*)$', views.groupadmin_app_complete, name="groupadmin_app_complete"),

    url(r'^admin/corp/audit/$', views.corpaudit_search, name="corpaudit_search"),
    url(r'^admin/corp/audit/([0-9]+)$', views.corpaudit_view, name="corpaudit_view"),

    url(r'^admin/assets/search/$', views.assetsearch_index, name="assetsearch_index"),

    url(r'^logistics/structures/$', views.structures_index, name="structures_index"),
    url(r'^logistics/structures/corp/([0-9]+)/([a-z]*)$', views.structures_list_corp, name="structures_list_corp"),
    url(r'^logistics/structures/system/([0-9]+)/([a-z]*)$', views.structures_list_system, name="structures_list_system"),
    url(r'^logistics/structures/([0-9]+)/state/([a-z]+)$', views.structures_fuelnotification_toggle, name="structures_fuelnotification_toggle"),

    url(r'^mumble/$', views.mumbleadmin_index, name="mumbleadmin_index"),
    url(r'^mumble/kick/([0-9]+)$', views.mumbleadmin_kick, name="mumbleadmin_kick"),

    url(r'^mumble/templinks/$', views.templink_index, name="templink_index"),
    url(r'^mumble/templinks/create/$', views.templink_create, name="templink_create"),
    url(r'^mumble/templinks/submit/$', views.templink_submit, name="templink_submit"),
    url(r'^mumble/templinks/disable/([0-9]+)$', views.templink_disable, name="templink_disable"),
    url(r'^mumble/templinks/([0-9A-Za-z]+)/$', views.templink_landing, name="templink_landing"),
    url(r'^mumble/templinks/([0-9A-Za-z]+)/submit$', views.templink_landing_submit, name="templink_landing_submit"),

    url(r'^settings/webhooks/$', views.settings_webhooks_index, name="settings_webhooks_index")
]
