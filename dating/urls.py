from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('profiles/', views.ProfileList.as_view(), name='profile_list'),
    path('profile/create/', views.ProfileCreate.as_view(), name='profile_create'),
]
