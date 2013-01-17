import string
import numpy as np
import networkx as nx
from apps.data.models import Match, Contribution
from networkx.algorithms.components.connected import connected_components
from sklearn.tree import DecisionTreeClassifier

########## GLOBALS ###########

CLASSIFIER_OBJ = DecisionTreeClassifier(compute_importances=True)

TRAINING_DATA = Match.objects.all().order_by('?')[:5000]

########### MAIN ##########

clf = CLASSIFIER_OBJ
clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

nameid = 0
first_letter_last_ln = ''
for ln in Contribution.objects.all().values('last_name').distinct()[:1000]:
    if not ln['last_name']:
        continue

    ln = ln['last_name']

    if ln[0] <> first_letter_last_ln:
        print ln[0]

    test = Match.objects.filter(c1__last_name=ln)

    #if len(test) == 1:
    #    test[0].classifier_id = nameid
    #    test[0].save()

    G = nx.Graph()

    for t in test:
        m = clf.predict_proba(eval(t.features))
        if m[0][1] > m[0][0]:
            G.add_edge(t.c1, t.c2)

    ccs = connected_components(G)
    print ccs

    for c in enumerate(ccs):
        did = c[0]
        for i in c[1]:
            i.classifier_id=int('%s%s' % (nameid, did))
            i.save()
    nameid += 1
    first_letter_last_ln = ln[0]