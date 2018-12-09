from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from manager.models import Account

# Create your views here.

class AccountListView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)
        return render(self.request, self.template_name, context)

