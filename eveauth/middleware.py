from avrseauth import local_settings


def auth_name_middleware(request):
    return {
        "AUTH_NAME": getattr(local_settings, "AUTH_NAME", "AVRSE Auth")
    }


def mumble_host(request):
    return {
        "MUMBLE": getattr(local_settings, "MUMBLE_HOST", None)
    }
