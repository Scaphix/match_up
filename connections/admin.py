from django.contrib import admin
from .models import Like, Match


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user1__username', 'user2__username']
    readonly_fields = ['created_at']
