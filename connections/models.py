from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Like(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    ACTION_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    from_user = models.ForeignKey(
                User, on_delete=models.CASCADE, related_name='likes_sent')
    to_user = models.ForeignKey(
                User, on_delete=models.CASCADE, related_name='likes_received')
    action = models.CharField(
                max_length=10, choices=ACTION_CHOICES, default=LIKE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        indexes = [
            models.Index(fields=['from_user', 'to_user']),
            models.Index(fields=['from_user', 'action']),
            models.Index(fields=['to_user', 'action']),
        ]

    def __str__(self):
        return f"{self.from_user.username} {self.action}s {self.to_user.username}"  # noqa: E501

    def save(self, *args, **kwargs):
        if self.from_user == self.to_user:
            raise ValueError("Users cannot like themselves")
        super().save(*args, **kwargs)


class Match(models.Model):
    user1 = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user1', 'user2'])]

    def __str__(self):
        return f"Match: {self.user1.username} & {self.user2.username}"

    def save(self, *args, **kwargs):
        # keep ordering stable to enforce uniqueness
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def get_other_user(self, user):
        return self.user2 if user == self.user1 else self.user1
