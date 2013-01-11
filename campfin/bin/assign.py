import string
import networkx as nx
from apps.fec.models import Match, Contribution
from networkx.algorithms.components.connected import connected_components
from sklearn.tree import DecisionTreeClassifier

training = Match.objects.filter(for_training=True)
training_correct = [int(t.same) for t in training]

nameid = 0
first_letter_last_ln = ''
for ln in Contribution.objects.all().values('last_name').distinct():
    ln = ln['last_name']

    if ln[0] <> first_letter_last_ln:
        print ln[0]

    test = Match.objects.filter(c1__last_name=ln, for_training=False)

    # If len(test) == 1: Assign its own ID. Else:

    clf = DecisionTreeClassifier(compute_importances=True)
    clf = clf.fit([eval(t.features) for t in training], training_correct)

    G = nx.Graph()

    for t in test:
        m = clf.predict_proba(eval(t.features))
        if m[0][1] > 0.0:
            G.add_edge(t.c1, t.c2)

    ccs = connected_components(G)

    for c in enumerate(ccs):
        did = c[0]
        for i in c[1]:
            i.donor_id=int('%s%s' % (nameid, did))
            i.save()
    nameid += 1
    first_letter_last_ln = ln[0]