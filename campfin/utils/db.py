'''
db.py

Helper functions to help with database saves in Django.
'''

from django.db import transaction

@transaction.commit_manually
def commit_saves(tosave_list):
    '''
    Allows manual transaction management for arbitrarily large updates.
    '''
    for item in tosave_list:
        item.save()
    transaction.commit()
    return