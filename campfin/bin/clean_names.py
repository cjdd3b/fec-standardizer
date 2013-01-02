from apps.fec.models import *

for i in Individual.objects.all():
    i.scrub()
