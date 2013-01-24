from django.contrib import admin
from apps.data.models import Match

########## ADMINS ##########

class MatchAdmin(admin.ModelAdmin):
    list_display = ['c1_repr', 'c2_repr', 'same', 'classifier_same', 'score', 'match_status']
    list_filter = ['same', 'match_status']
    list_editable = ['same']
    search_fields = ['c1__contributor_name', 'c2__contributor_name']

    def c1_repr(self, obj):
        '''
        Allows us to use property from the related model in the admin.
        '''
        return obj.c1.match_repr

    def c2_repr(self, obj):
        return obj.c2.match_repr

admin.site.register(Match, MatchAdmin)