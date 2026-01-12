from django.shortcuts import render
from core.context import base_context


def public_about(request):
    context = {}
    context.update(base_context(request, public=True))

    return render(
        request,
        "public/about.html",
        context
    )
