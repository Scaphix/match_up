from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(99)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    interests = models.CharField(max_length=250, blank=True)
    photo = CloudinaryField(
        'image', folder='profile_pictures/', blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    is_profile_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def complete_profile(self, *args, **kwargs):
        # Check if profile is complete
        self.is_profile_complete = bool(
            self.bio and
            self.age and
            self.gender and
            self.location and
            self.interests and
            self.photo
        )
        super().save(*args, **kwargs)
