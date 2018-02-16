from django import template

register = template.Library()


@register.filter(name="user_can_edit")
def user_can_edit(timer, user):
    return timer.user_can_edit(user)

@register.filter(name="side_class")
def side_class(timer):
    return "text-" + [
        "info",
        "danger",
        'warning'
    ][timer.side]