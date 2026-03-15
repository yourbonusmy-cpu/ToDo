from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import TaskTemplateForm


@login_required
def task_template_create(request):
    if request.method == "POST":
        form = TaskTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect("/task-template/create/")
    else:
        form = TaskTemplateForm()

    return render(
        request,
        "core/task_template_create.html",
        {"form": form},
    )
