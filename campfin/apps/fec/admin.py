from django.contrib import admin
from campfin.apps.fec.models import Match

########## ADMINS ##########

class MatchAdmin(admin.ModelAdmin):
    list_display = ['i1_test', 'i2_test', 'same', 'for_training', 'score']
    list_filter = ['same', 'for_training']
    list_editable = ['same', 'for_training']
admin.site.register(Match, MatchAdmin)