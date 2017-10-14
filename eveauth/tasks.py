from avrseauth.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from avrseauth.settings import members, blues
from django.conf import settings

from models.character import Character
from models.corporation import Corporation
from models.alliance import Alliance
from models.templink import Templink
from esi import ESI
from ipb import IPBUser
from discord.api import DiscordAPI


def get_server():
    import Ice
    Ice.loadSlice( '', ['-I' + Ice.getSliceDir(), "eveauth/Murmur.ice"])
    import Murmur

    ice = Ice.initialize()
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h 127.0.0.1 -p 6502'))
    server = meta.getServer(1)
    return server


# Update user groups from the API
@app.task(name="spawn_groupupdates")
def spawn_groupupdates():
    users = User.objects.all()
    for user in users:
        update_groups.delay(user.id)

    print "Spawned group update tasks for %s users" % users.count()



# Set expired templinks inactive and kick anyone using them from mumble
@app.task(name="purge_expired_templinks")
def purge_expired_templinks():
    templinks = Templink.objects.filter(
        active=True,
        expires__lt=timezone.now()
    ).all()

    for templink in templinks:
        templink.active = False
        templink.save()

        purge_templink_users.delay(templink.id, reason="Templink expired")

        print "Purged templink [%s] %s" % (templink.tag, templink.link)


# Move people to mumble
@app.task(name="mumble_afk_check")
def mumble_afk_check():
    if settings.MUMBLE_AUTO_AFK:
        server = get_server()
        users = server.getUsers().items()

        for session, user in users:
            if (user.selfDeaf and user.idlesecs >= settings.MUMBLE_AUTO_AFK_DELAY) or user.idlesecs >= 7200:
                if user.channel != settings.MUMBLE_AUTO_AFK_CHANNEL:
                    # Move the user to the afk channel
                    user.channel = settings.MUMBLE_AUTO_AFK_CHANNEL
                    server.setState(user)

        server.ice_getCommunicator().destroy()



# Purge all users using a particular templink
@app.task(name="purge_templink_users")
def purge_templink_users(templink_id, reason="Templink deactivated"):
    server = get_server()

    # Get templink user list
    templink = Templink.objects.get(id=templink_id)
    id_map = map(lambda x: x.mumble_id(), templink.users.all())

    # Get active user list from server
    users = server.getUsers().items()

    # Get a list of active users using this temp link
    user_map = filter(lambda x: x.userid in id_map, map(lambda x: x[1], users))

    # Kick each user from the server
    for user in user_map:
        server.kickUser(user.session, reason)

    server.ice_getCommunicator().destroy()



# Update a users groups from the API
@app.task(name="update_groups")
def update_groups(user_id):
    user = User.objects.get(id=user_id)
    print "Updating groups for %s" % user.username
    social = user.social_auth.filter(provider="eveonline").first()

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

    # Update IPB User
    if user.profile.forum_id:
        ipb = IPBUser(user)
        ipb.update_access_level()

    update_discord.delay(user.id)


# Update Discord status
@app.task(name="update_discord")
def update_discord(user_id):
    user = User.objects.get(id=user_id)
    print "Updating discord for %s" % user.username

    social_discord = user.social_auth.filter(provider="discord").first()
    if social_discord != None:
        api = DiscordAPI()

        # Check if the user is on discord
        if api.is_user_in_guild(social_discord.uid):
            # Check if we should kick the user
            if user.profile.level < settings.DISCORD_ACCESS_LEVEL:
                api.kick_member(social_discord.uid)
                return

            # Update the users name
            api.set_name(social_discord.uid, user.profile.character.name)

            # Update the users roles
            roles = [
                user.profile.corporation.ticker,
                ["Non-member", "Blue", "Member"][user.profile.level]
            ]
            groups = user.groups.exclude(
                Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")
            ).all()
            for group in groups:
                roles.append(group.name)
            print "Updating roles: %s" % str(roles)
            api.update_roles(social_discord.uid, roles)
