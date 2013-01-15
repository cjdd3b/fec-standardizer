import networkx as nx
from apps.data.models import DemoMatch
from networkx.algorithms.components.connected import connected_components
from sklearn.tree import DecisionTreeClassifier

pool = DemoMatch.objects.all().order_by('?')
training = pool[:5000]
test = pool[5000:]
training_correct = [int(t.same) for t in training]

clf = DecisionTreeClassifier(compute_importances=True)
clf = clf.fit([eval(t.features) for t in training], training_correct)

G = nx.Graph()
tp, fp, tn, fn, total = 0, 0, 0, 0, 0
for t in test:
    same = False
    total += 1
    m = clf.predict_proba(eval(t.features))
    if m[0][1] > 0.0:
        same = True
        G.add_edge(t.c1.pk, t.c2.pk)

    if same == True and t.same == True:
        tp += 1
    elif same == True and t.same == False:
        #print 'False positive: %s %s' % (t, str(m))
        fp += 1
    elif same == False and t.same == True:
        #print 'False negative: %s %s' % (t, str(m))
        fn += 1
    else:
        tn += 1

precision = float(tp) / (float(tp) + float(fp))
recall = float(tp) / (float(tp) + float(fn))

print '---------- EVALUATION METRICS ----------'
print 'True positives: %s' % tp
print 'False positives: %s' % fp
print 'False negatives: %s' % fn
print 'True negatives: %s' % tn
print 'Precision: %s' % precision
print 'Recall: %s' % recall
print 'F1: %s' % str(2 * ((precision * recall) / (precision + recall)))

#for g in connected_components(G):
#    print '---------- CLUSTER ----------'
#    for h in g:
#        print Individual.objects.get(pk=h)
#    print '\n'

#print '---------- FEATURE IMPORTANCES ----------'
#print clf.feature_importances_