from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('profiles/', views.ProfileList.as_view(), name='profile_list'),
    path(
        'profile/getstarted/',
        views.ProfileGetStarted.as_view(),
        name='profile_getstarted',
    ),
    path(
        'profile/create/',
        views.ProfileCreate.as_view(),
        name='profile_create',
    ),
    path(
        'profile/edit/',
        views.ProfileUpdate.as_view(),
        name='profile_update',
    ),
    path(
        'profile/delete/',
        views.ProfileDelete.as_view(),
        name='profile_delete',
    ),
    path(
        'profile/about/',
        views.ProfileAbout.as_view(),
        name='profile_about',
    ),
    path(
        'profile/<int:pk>/',
        views.ProfileDetail.as_view(),
        name='profile_detail',
    ),
    path(
        'preferences/create/',
        views.PreferenceCreate.as_view(),
        name='preference_create',
    ),
    path(
        'preferences/edit/',
        views.PreferenceUpdate.as_view(),
        name='preference_update',
    ),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
