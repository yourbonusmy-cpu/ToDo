from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def stats_weekdays_page(request):
    return render(request, "core/stats_weekdays.html")
