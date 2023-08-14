from django.contrib import admin
from .models import User, Match, Prediction

#admin.site.register(User)
#admin.site.register(Match)
#admin.site.register(Prediction) 

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_time', 'round', 'home_team', 'away_team', 'status')
    list_filter = ('round', 'home_team', 'away_team', 'status')
    search_fields = ('home_team', 'away_team')
    ordering = ('match_time',)
    actions = ('change_to_scheduled', 'change_to_postponed')
    
    @admin.action(description='Change to Scheduled')
    def change_to_scheduled(self, request, queryset):
        queryset.update(status='S')
    
    @admin.action(description='Change to Postponed')
    def change_to_postponed(self, request, queryset):
        queryset.update(status='P')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'userid')
    search_fields = ('name', 'email')
    ordering = ('name',)

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'points')
    list_filter = ('user',)
    ordering = ('user',)

