from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from eveauth.models import Requirement, RequirementSkill
from eveauth.forms import RequirementForm, RequirementSkillForm

from sde.models import Type


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
        delete = True
    else:
        instance = None
        delete = False

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
        "delete": delete
    }
    return render(request, "eveauth/edit_form.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "HR"]).exists())
def manage_requirement_skills(request, requirement_id):
    requirement = get_object_or_404(Requirement, id=requirement_id)
    requirement.skills.prefetch_related('skill').all()

    context = {
        "requirement": requirement
    }
    return render(request, "eveauth/requirements/manage_requirement_skills.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "HR"]).exists())
def edit_requirement_skill(request, requirement_id, skill_id=None):
    requirement = get_object_or_404(Requirement, id=requirement_id)
    if skill_id is not None:
        instance = get_object_or_404(RequirementSkill, id=skill_id)
        delete = True
    else:
        instance = None
        delete = False

    if request.method == "POST":
        form = RequirementSkillForm(request.POST, instance=instance)
        if form.is_valid():
            if "delete" in request.POST:
                form.instance.delete()
                return redirect("manage_requirement_skills", requirement.id)

            try:
                form.instance.requirement = requirement
                form.save()

                if "save_and_close" in request.POST:
                    return redirect("manage_requirement_skills", requirement.id)
                else:
                    return redirect("edit_requirement_skill", requirement.id, form.instance.id)
            except IntegrityError:
                messages.error(request, "There's already an entry for that skill on this requirement.")
    else:
        form = RequirementSkillForm(instance=instance)

    context = {
        "name": "Requirement",
        "form": form,
        "delete": delete
    }
    return render(request, "eveauth/edit_form.html", context)