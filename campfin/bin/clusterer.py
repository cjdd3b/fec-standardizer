from lsh.lsh import Cluster, shingle
from apps.fec.models import Individual, Group

cluster = Cluster(threshold=0.75)
for name in Individual.objects.all():
    try:
        cluster.add_set(shingle(name.clean_name, 3), name)
    except: # Ultimately gotta figure out and fix all this
        pass
        #print name

for item in enumerate(cluster.get_sets()):
    label=item[0]
    g = Group(label=1, count=len(item[1]))
    g.save()
    for indiv in item[1]:
        indiv.group = g
        indiv.save()