from avrseauth import local_settings


def auth_name_middleware(request):
    return {
        "AUTH_NAME": getattr(local_settings, "AUTH_NAME", "AVRSE Auth")
    }
