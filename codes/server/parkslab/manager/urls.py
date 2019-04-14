from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('index/', views.AccountListView.as_view(), name='index'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user/<int:user_profile_id>/home/',views.UserProfileView.home, name='user_home'),
    path('project/search/', views.ProjectIndex.project_search, name='project_search'),
    path('explore/', views.project_explore, name='project_explore'),
    path('explore2/', views.project_explore2, name='project_explore2'),
]