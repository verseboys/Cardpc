from django.shortcuts import render

from natureself.django.core.decorators import private_network_required

@private_network_required
def preview_email_template(request):
    template = request.GET.get('template')
    context = { k: v for k, v in request.GET.items()}
    return render(request, template, context)
