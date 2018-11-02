from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from eveauth.models import Requirement, RequirementSkill
from eveauth.forms import RequirementForm


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "HR"]).exists())
def manage_requirements(request):
    requirements = Requirement.objects.prefetch_related("skills").order_by("name")

    context = {
        "requirements": requirements
    }
    return render(request, "eveauth/requirements/manage_requirements.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "HR"]).exists())
def edit_requirement(request, requirement_id=None):
    if requirement_id is not None:
        instance = get_object_or_404(Requirement, id=requirement_id)
    else:
        instance = None

    if request.method == "POST":
        form = RequirementForm(request.POST, instance=instance)
        if form.is_valid():
            if "delete" in request.POST:
                form.instance.delete()
                return redirect("manage_requirements")

            form.save()
            if "save_and_close" in request.POST:
                return redirect("manage_requirements")
            else:
                return redirect("edit_requirement", form.instance.id)
    else:
        form = RequirementForm(instance=instance)

    context = {
        "name": "Requirement",
        "form": form,
    }
    return render(request, "eveauth/edit_form.html", context)