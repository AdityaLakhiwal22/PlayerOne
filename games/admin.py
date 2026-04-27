from django.contrib import admin
from .models import GamePost, JoinRequest, Comment, PlayerProfile

@admin.register(GamePost)
class GamePostAdmin(admin.ModelAdmin):
    list_display = ['title', 'sport', 'mode', 'city', 'status', 'posted_by', 'created_at']
    list_filter = ['mode', 'sport', 'status']
    search_fields = ['title', 'city']

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ['player', 'game_post', 'status', 'created_at']
    list_filter = ['status']

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'area', 'reputation']

admin.site.register(Comment)
