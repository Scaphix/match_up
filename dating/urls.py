from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('profiles/', views.ProfileList.as_view(), name='profile_list'),
    path('profile/create/', views.ProfileCreate.as_view(), name='profile_create'),
    path('profile/about/', views.ProfileAbout.as_view(), name='profile_about'),
    path('profile/<int:pk>/', views.ProfileDetail.as_view(), name='profile_detail'),
]
