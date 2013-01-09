from apps.fec.models import Match

#for m in Match.objects.filter(for_training=False):
#    m.for_training = True
#    m.score = 10.0
#    m.same = False
#    m.save()

#for m in Match.objects.filter(for_training=True, same=None):
#    m.score = 10.0
#    m.same = False
#    m.save()

for m in Match.objects.filter(score=10.0):
    m.score = None
    m.save()
