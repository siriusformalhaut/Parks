from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from manager.models import Account

# Create your views here.

class AccountListView(TemplateView):
    template_name = "worker_list.html"

    def get(self, request, *args, **kwargs):
        context = super(AccountListView, self)
        return render(self.request, self.template_name, context)
