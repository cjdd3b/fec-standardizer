from django.db import transaction

@transaction.commit_manually
def commit_saves(tosave_list):
    for item in tosave_list:
        item.save()
    transaction.commit()
    return