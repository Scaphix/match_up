"""
Service functions for connection-related operations
"""
from dating.models import Profile
from .models import Like


def get_discoverable_profiles(user, preferences=None, order_by='newest'):
    """
    Get profiles that are discoverable for a user based on their preferences
    and interaction history.

    Args:
        user: The User instance requesting discoverable profiles
        preferences: Optional Preference instance. If None, will try to get
                     from user.preference or use defaults
        order_by: 'newest' (default) or 'random' for ordering

    Returns:
        QuerySet of Profile objects that match the criteria
    """

    # Start with all profiles except current user
    queryset = Profile.objects.exclude(user=user)

    # Exclude profiles user has already liked
    liked_user_ids = Like.objects.filter(
        from_user=user,
        action=Like.LIKE
    ).values_list('to_user_id', flat=True)
    queryset = queryset.exclude(user_id__in=liked_user_ids)

    # Exclude profiles user has already passed/disliked
    disliked_user_ids = Like.objects.filter(
        from_user=user,
        action=Like.DISLIKE
    ).values_list('to_user_id', flat=True)
    queryset = queryset.exclude(user_id__in=disliked_user_ids)

    # Apply ordering
    if order_by == 'random':
        queryset = queryset.order_by('?')
    else:  # default to 'newest'
        queryset = queryset.order_by('-createdAt')

    return queryset
