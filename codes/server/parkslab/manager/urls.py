from django.urls import path
from django.contrib import admin
from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='index'),
    path('mypage/', views.LoginView.as_view(), name='mypage'),
     path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('project/search/', views.project_search, name='project_search'),
]