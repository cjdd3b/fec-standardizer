import string
import networkx as nx
from apps.fec.models import Match, Individual, Contribution
from networkx.algorithms.components.connected import connected_components
from sklearn.tree import DecisionTreeClassifier

training = Match.objects.filter(for_training=True)
training_correct = [int(t.same) for t in training]

for letter in string.uppercase:
    print "Processing %s" % letter
    test = Match.objects.filter(i1__last_name__startswith='BANKS', for_training=False)

    clf = DecisionTreeClassifier(compute_importances=True)
    clf = clf.fit([eval(t.features) for t in training], training_correct)

    G = nx.Graph()

    for t in test:
        m = clf.predict_proba(eval(t.features))
        if m[0][1] > 0.0:
            G.add_edge(t.i1, t.i2)

    ccs = connected_components(G)

    for c in enumerate(ccs):
        did = c[0]
        for i in c[1]:
            contribs = Contribution.objects.filter(contributor_name=i.contributor_name, city=i.city, state=i.state, employer=i.employer, occupation=i.occupation)
            contribs.update(donor_id=did)