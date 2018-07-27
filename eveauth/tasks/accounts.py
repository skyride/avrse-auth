from django.contrib.auth.models import User
from django.db import transaction

from avrseauth.celery import app
from avrseauth.settings import members, blues

from eveauth import ipb
from eveauth.esi import ESI
from eveauth.models.alliance import Alliance
from eveauth.models.character import Character
from eveauth.models.corporation import Corporation


# Update user groups from the API
@app.task(name="spawn_groupupdates", expires=3600)
def spawn_groupupdates():
    users = User.objects.all()
    for user in users:
        update_groups.delay(user.id)

    print "Spawned group update tasks for %s users" % users.count()
    return users.count()


# Update a users groups from the API
@app.task(name="update_groups", expires=3600)
def update_groups(user_id):
    from .characters import update_character
    from .services import update_discord

    user = User.objects.get(id=user_id)
    print "Updating groups for %s" % user.username
    social = user.social_auth.filter(provider="eveonline").first()

    # Queue character updates
    for char in user.characters.all():
        update_character.delay(char.id)

    # Update char/corp/alliance
    api = ESI()
    char_id = social.extra_data['id']
    char = api.get("/v4/characters/%s/" % char_id)

    with transaction.atomic():
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
        char_id = user.profile.character_id
        corp_id = user.profile.corporation_id
        alliance_id = user.profile.alliance_id

        if corp_id in members['corps'] or alliance_id in members['alliances'] or char_id in members['chars']:
            user.profile.level = 2
        elif corp_id in blues['corps'] or alliance_id in blues['alliances'] or char_id in blues['chars']:
            user.profile.level = 1
        else:
            user.profile.level = 0

        user.profile.save()

        # Check groups are still valid with access level
        for group in user.groups.filter(details__access_level__gt=user.profile.level):
            user.groups.remove(group)

    # Update IPB User
    if ipb.is_active():
        if user.profile.forum_id:
            forum_api = ipb.IPBUser(user)
            forum_api.update_access_level()

    update_discord.delay(user.id)