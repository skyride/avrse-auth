from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from flarum.api import FlarumAPI
from flarum.exceptions import Flarum4XXClientError
from flarum.operations import create_user
from flarum.models import FlarumUser
from flarum.tasks import update_users_groups


class UpdatePasswordView(View):
    """Receives a submission from the flarum password forum"""
    def post(self, request):
        from eveauth.views import services
        
        try:
            flarum = request.user.flarum
            api = FlarumAPI()
            api.update_user_password(request.user.id, request.POST['password'])
            messages.success(request, "Updated forum password")
        except FlarumUser.DoesNotExist:
            try:
                flarum = create_user(request.user, request.POST['password'])
                messages.success(request, "Created forum account")
                update_users_groups(flarum.id)
            except Flarum4XXClientError:
                messages.error(request, "Password was invalid, make sure it has at least 8 characters")

        return redirect(services)