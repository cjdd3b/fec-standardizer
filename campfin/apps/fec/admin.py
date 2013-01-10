from django.contrib import admin
from campfin.apps.fec.models import Match

########## ADMINS ##########

class MatchAdmin(admin.ModelAdmin):
    list_display = ['c1_string', 'c2_string', 'same', 'for_training', 'score']
    list_filter = ['same', 'for_training']
    list_editable = ['same', 'for_training']
    search_fields = ['c1__contributor_name', 'c2__contributor_name']
admin.site.register(Match, MatchAdmin)