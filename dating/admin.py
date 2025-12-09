from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'location', 'bio', 'interests', 'photo')
    list_filter = ('age', 'gender', 'location')
    search_fields = ('user__username', 'user__email')
