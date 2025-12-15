from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator, MaxValueValidator, MinLengthValidator
)
from django.core.exceptions import ValidationError
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
    bio = models.TextField(max_length=500, validators=[MinLengthValidator(10)])
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


class Preference(models.Model):
    """
    User matching preferences for discovery feed filtering
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='preference'
    )
    min_age = models.PositiveIntegerField(
        default=18,
        validators=[MinValueValidator(18), MaxValueValidator(99)]
    )
    max_age = models.PositiveIntegerField(
        default=99,
        validators=[MinValueValidator(18), MaxValueValidator(99)]
    )
    preferred_genders = models.CharField(
        max_length=10,
        default='M,F,O',
        help_text='Comma-separated list: M, F, O'
    )
    max_distance = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Maximum distance in km (optional, for future geolocation)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Preferences"

    def clean(self):
        """Validate that min_age is less than max_age"""
        if self.min_age >= self.max_age:
            raise ValidationError(
                {'min_age': 'Minimum age must be less than maximum age.'}
            )

    def save(self, *args, **kwargs):
        """Call clean validation before saving"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_preferred_genders_list(self):
        """Return preferred genders as a list"""
        return [g.strip() for g in self.preferred_genders.split(',')]
