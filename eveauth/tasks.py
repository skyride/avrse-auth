from avrseauth.celery import app
from django.contrib.auth.models import User
from avrseauth.local_settings import members, blues

from models.character import Character
from models.corporation import Corporation
from models.alliance import Alliance
from esi import ESI


@app.task(name="update_groups")
def update_groups(user_id):
    user = User.objects.get(id=user_id)
    social = user.social_auth.get(provider="eveonline")

    # Update char/corp/alliance
    api = ESI()
    char_id = social.extra_data['id']
    char = api.get("/characters/%s/" % char_id)

    user.profile.character = Character.get_or_create(char_id)
    user.profile.corporation = Corporation.get_or_create(char['corporation_id'])
    if "alliance_id" in char:
        user.profile.alliance = Alliance.get_or_create(char['alliance_id'])
    else:
        user.profile.alliance = None


    # Update groups
    for group in user.groups.filter(name__startswith="Corp: ").all():
        user.groups.remove(group)
    for group in user.groups.filter(name__startswith="Alliance: ").all():
        user.groups.remove(group)

    if user.profile.corporation != None:
        user.groups.add(user.profile.corporation.group)
    if user.profile.alliance != None:
        user.groups.add(user.profile.alliance.group)


    # Update access level
    corp_id = user.profile.corporation_id
    alliance_id = user.profile.alliance_id

    if corp_id in members['corps'] or alliance_id in members['alliances']:
        user.profile.level = 2
    elif corp_id in blues['corps'] or alliance_id in blues['alliances']:
        user.profile.level = 1
    else:
        user.profile.level = 0

    user.profile.save()
