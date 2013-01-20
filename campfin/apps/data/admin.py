from django.contrib import admin
from apps.data.models import Match

########## ADMINS ##########

class MatchAdmin(admin.ModelAdmin):
    list_display = ['c1_string', 'c2_string', 'same', 'classifier_same', 'score', 'match_status']
    list_filter = ['same', 'match_status']
    list_editable = ['same']
    search_fields = ['c1__contributor_name', 'c2__contributor_name']
admin.site.register(Match, MatchAdmin)