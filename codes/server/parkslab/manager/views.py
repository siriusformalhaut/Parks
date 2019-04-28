from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from manager.models import UserAccount, Project, CategoryM

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, ProjectSearchForm
)
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect

import operator
from functools import reduce

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import random
import math

User = get_user_model()
# Create your views here.

class AccountListView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)
        return render(self.request, self.template_name, context)
    
    def post(self, _, *args, **kwargs):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect(self.get_next_redirect_url())
        else:
            kwargs = {'template_name': 'login.html'}
            return login(self.request, *args, **kwargs)

    def get_next_redirect_url(self):
        redirect_url = self.request.GET.get('next')
        if not redirect_url or redirect_url == '/':
            redirect_url = '/worker_list/'
        return redirect_url

class CustomLoginView(TemplateView):
    template_name = "login.html"

    def get(self, _, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(self.get_next_redirect_url())
        else:
            kwargs = {'template_name': 'login.html'}
            return login(self.request, *args, **kwargs)

    def post(self, _, *args, **kwargs):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)  # 1
        if user is not None:
            login(self.request, user)
            return redirect(self.get_next_redirect_url())
        else:
            kwargs = {'template_name': 'login.html'}
            return login(self.request, *args, **kwargs)

    def get_next_redirect_url(self):
        redirect_url = self.request.GET.get('next')
        if not redirect_url or redirect_url == '/':
            redirect_url = '/worker_list/'
        return redirect_url

class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('manager/mail_templates/user_create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('manager/mail_templates/user_create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('manager:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*3)  # デフォルトでは3h以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

def paginate_queryset(request, queryset, count):
    """return a page object"""
    #divide queryset into pages
    paginator = Paginator(queryset, count)
    #get the number of current page
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

class ProjectIndex(generic.ListView):
    """Search & Explore Projects"""
    model = Project
    #number of items in one page
    paginate_by = 10

    @csrf_protect
    def project_search(request):
        """Search Projects"""
        # create an empty form
        form = ProjectSearchForm()
        # fetch all data of projects
        projects = Project.objects.all()
        # dictionary of projects and sort order
        ex_projects = []
        for project in projects:
            ex_projects.append({
                'project': project,
                'numinclkeywords': 1
            })
        # When the search button is pushed
        if request.method == 'POST':
            # fetch the form data
            form = ProjectSearchForm(request.POST)
            projects = Project.objects.all()
        if form.is_valid():
            # split the inputed data into keywords
            keywords = form.cleaned_data['keyword'].split()
            # make query from keywords: "and" combination of (keyword1 in name or details)
            query = reduce(operator.or_, ((Q(name__contains=keyword)|Q(details__contains=keyword)|Q(categories__name__contains=keyword)) for keyword in keywords))
            # fetch the project data with the query
            projects = list(set(Project.objects.filter(query)))
            # count how many keywords each project contains
            ex_projects.clear()
            for project in projects:
                numinclkeywords = 0
                for keyword in keywords:
                    if (keyword in project.name)|(keyword in project.details):
                        numinclkeywords += 1
                    else:
                        ifkwincat = False
                        for category in project.categories.all():
                            if keyword in category.name:
                                ifkwincat = True
                                break
                        if ifkwincat:
                            numinclkeywords += 1
                ex_projects.append({
                    'project': project,
                    'numinclkeywords': numinclkeywords
                })
        # sort projects
        projects_sorted = sorted(ex_projects, key=lambda x:x['numinclkeywords'], reverse=True)
        # paging
        page_obj = paginate_queryset(request, projects_sorted, ProjectIndex.paginate_by)
        # generate the context
        context = {
            'form':form,
            'page_obj':page_obj,
        }
        # render project_search.html with the fetched project data
        return render(request,
                      'project_search.html',
                      context)

    def project_explore(request):
        return render(request, 'project_explore.html')

    def project_explore2(request):
        categories = CategoryM.objects.all()
        ExCategories = []
        idbuf = 0
        Occupied = []
        MaxHorizontal = 6
        MaxVertical = 2
        MaxRadius = 160
        MaxDisplay = MaxHorizontal*MaxVertical
        Passed = 0
        CatLen = len(categories)

        categories = paginate_queryset(request, categories, MaxDisplay)

        for category in categories:
            for i in range(MaxDisplay):
                radiusbuf = random.uniform(40, 80)
                leftbuf = random.uniform(0, MaxRadius*MaxHorizontal)
                topbuf = random.uniform(100, 100+MaxRadius*MaxVertical)
                leftint = math.floor(leftbuf/MaxRadius)
                topint = math.floor((topbuf-100)/MaxRadius)
                posbuf = {
                          'left':leftint,
                          'top':topint,
                }
                if posbuf in Occupied:
                    continue
                else:
                    Occupied.append(posbuf)
                    leftbuf = leftint*160 + random.uniform(radiusbuf, MaxRadius-radiusbuf)
                    topbuf = topint*160 + 100 + random.uniform(radiusbuf, MaxRadius-radiusbuf)
                    break
            ExCategories.append({"name":category.name,
                                 "left":leftbuf,
                                 "top":topbuf,
                                 "radius":radiusbuf,
                                 "id":idbuf
                                })
            idbuf = idbuf + 1
        context = {
            'categories':ExCategories,
        }
        return render(request,
                      'project_explore2.html',
                      context)
