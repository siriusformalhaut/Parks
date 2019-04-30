from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('index/', views.AccountListView.as_view(), name='index'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('project/search/', views.ProjectSearch.project_search, name='project_search'),
    path('project/explore/', views.ProjectExplore.project_explore2, name='project_explore2'),
]