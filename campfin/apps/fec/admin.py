from django.contrib import admin
from campfin.apps.fec.models import Match

########## ADMINS ##########

class MatchAdmin(admin.ModelAdmin):
    list_display = ['i1_test', 'i2_test', 'features', 'same', 'for_training', 'score']
    list_filter = ['same', 'for_training']
    list_editable = ['same', 'for_training']
    search_fields = ['i1__contributor_name', 'i2__contributor_name']
admin.site.register(Match, MatchAdmin)