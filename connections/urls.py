from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    path(
        'discover/', views.DiscoverView.as_view(), name='discover'
        ),
    path(
        'like/<int:profile_id>/',
        views.LikeProfileView.as_view(),
        name='like_profile'),
    path(
        'pass/<int:profile_id>/',
        views.PassProfileView.as_view(),
        name='pass_profile'),
    path(
        'dislike/<int:profile_id>/',
        views.PassProfileView.as_view(),
        name='dislike_profile'),
    path(
        'liked/',
        views.LikedProfilesView.as_view(),
        name='liked_profiles'),
    path(
        'matches/',
        views.MatchesListView.as_view(),
        name='matches'),
]
