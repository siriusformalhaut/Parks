"""parkslab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include, url

import manager.views as manager_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', manager_view.CustomLoginView.as_view()),
    #url(r'^logout/', manager_view.logout_view),
    #url(r'^worker_list/', login_required(manager_view.WorkerListView.as_view())),
    url(r'^hijack/', include('hijack.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', manager_view.AccountListView.as_view())
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('manager.urls')),
]
