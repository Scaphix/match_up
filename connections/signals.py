from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Match


@receiver(post_save, sender=Like)
def create_match_on_mutual_like(sender, instance, created, **kwargs):
    """
    Automatically create a Match when two users like each other.
    This signal fires after a Like is saved.
    """
    # Only process if this is a new Like with action='like'
    if not created or instance.action != Like.LIKE:
        return

    # Check if the other user has also liked this user back
    reverse_like = Like.objects.filter(
        from_user=instance.to_user,
        to_user=instance.from_user,
        action=Like.LIKE
    ).first()

    if reverse_like:
        # Mutual like exists - create a Match
        # Ensure stable ordering (user1.id < user2.id) for uniqueness
        user1, user2 = instance.from_user, instance.to_user
        if user1.id > user2.id:
            user1, user2 = user2, user1

        # Use get_or_create to prevent duplicate matches
        Match.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={'is_active': True}
        )
