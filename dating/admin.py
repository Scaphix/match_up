from django.contrib import admin
from .models import Profile
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Profile)
class ProfileAdmin(SummernoteModelAdmin):
    list_display = (
        'user', 'age', 'gender', 'location', 'bio', 'interests', 'photo'
    )
    list_filter = ('age', 'gender', 'location')
    search_fields = ('user__username', 'user__email')
    summernote_fields = ('bio', 'interests')
