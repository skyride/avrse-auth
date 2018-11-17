from django.contrib.auth.models import Group, User
from django.conf import settings
from django.db.models import Q

from avrseauth.celery import app

from flarum.api import FlarumAPI
from flarum.models import FlarumUser, FlarumGroup
from flarum.operations import get_or_create_group

from eveauth.models import Corporation, Alliance


@app.task(name="sync_groups_and_users", expires=3600)
def sync_groups_and_users():
    """
    Fetches latest state for existing users then applies expected state to all users
    and groups
    """
    if settings.FLARUM_URL != "":
        # Fetch existing data
        api = FlarumAPI()
        groups = api.get("/groups").json()['data']
        for group in groups:
            if int(group['id']) != 3:
                db_group, created = FlarumGroup.objects.update_or_create(
                    id=group['id'],
                    defaults={
                        "name_singular": group['attributes']['nameSingular'],
                        "name_plural": group['attributes']['namePlural']
                    }
                )
                if created:
                    # See if we can set the type accurately
                    if db_group.name_singular.lower() in ['member', 'blue', 'non-member']:
                        db_group.type = "access_level"
                    elif Corporation.objects.filter(ticker=db_group.name_singular).exists():
                        db_group.type = "corp"
                    elif Alliance.objects.filter(ticker=db_group.name_singular).exists():
                        db_group.type = "alliance"
                    elif Group.objects.filter(name=db_group.name_singular).exists():
                        db_group.type = "group"
                        db_group.group = Group.objects.get(name=db_group.name_singular)
                    else:
                        db_group.type = "forum_group"
                    db_group.save()

        users = api.get("/users").json()['data']
        for user in users:
            db_user, created = FlarumUser.objects.update_or_create(
                id=user['id'],
                defaults={
                    "username": user['attributes']['username'],
                    "email": user['attributes']['email']
                }
            )

        # Create access level groups
        get_or_create_group("Member", "Members", "access_level")
        get_or_create_group("Blue", "Blues", "access_level")
        get_or_create_group("Non-member", "Non-members", "access_level")

        # Update user groups
        for user in FlarumUser.objects.filter(user__isnull=False):
            update_users_groups(user.id)


@app.task(name="update_users_groups", expires=3600)
def update_users_groups(flarum_user_id):
    api = FlarumAPI()
    user = FlarumUser.objects.get(id=flarum_user_id)
    groups = []
    # Access Level
    groups.append(
        FlarumGroup.objects.get(name_singular=["Non-member", "Blue", "Member"][user.user.profile.level])
    )

    # Corp
    corp = user.user.profile.corporation
    if corp is not None:
        groups.append(get_or_create_group(corp.ticker, corp.ticker, "corp"))

    # Alliance
    alliance = user.user.profile.alliance
    if alliance is not None:
        groups.append(get_or_create_group(alliance.ticker, alliance.ticker, "alliance"))

    # Groups
    for group in user.user.groups.exclude(Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")):
        groups.append(get_or_create_group(group.name, group.name, "group"))

    api.update_user_groups(user.id, groups)