from avrseauth import local_settings


def global_vars(request):
    return {
        "AUTH_NAME": getattr(local_settings, "AUTH_NAME", "AVRSE Auth"),
        "MUMBLE": getattr(local_settings, "MUMBLE_HOST", None),
        "DEBUG": getattr(local_settings, "DEBUG", False)
    }
