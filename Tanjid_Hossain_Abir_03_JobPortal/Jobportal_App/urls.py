from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('post-job/', views.post_job, name='post_job'),
    path('job-search/', views.job_search, name='job_search'),
    path('skill-matching-dashboard/', views.skill_matching_dashboard, name='skill_matching_dashboard'),
]
