from django.contrib import admin
from .models import Profile, Preference
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Profile)
class ProfileAdmin(SummernoteModelAdmin):
    list_display = (
        'user', 'age', 'gender', 'location', 'bio', 'interests', 'photo'
    )
    list_filter = ('age', 'gender', 'location')
    search_fields = ('user__username', 'user__email')
    summernote_fields = ('bio', 'interests')


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'min_age', 'max_age', 'preferred_genders', 'max_distance',
        'created_at'
    )
    list_filter = ('min_age', 'max_age', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Age Preferences', {
            'fields': ('min_age', 'max_age')
        }),
        ('Gender Preferences', {
            'fields': ('preferred_genders',)
        }),
        ('Distance (Optional)', {
            'fields': ('max_distance',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
