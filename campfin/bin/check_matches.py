import sys
import networkx as nx
from django.db import transaction
from django.db.models import F
from sklearn.tree import DecisionTreeClassifier
from apps.data.models import Match, Contribution

########## GLOBALS ##########

LOAD = True

########## HELPER FUNCTIONS ##########

@transaction.commit_manually
def commit_saves(tosave_list):
    for item in tosave_list:
        item.save()
    transaction.commit()
    return

########## TESTS ##########

def load_data():
    clf = DecisionTreeClassifier(compute_importances=True)
    train = Match.objects.all().order_by('?')[:5000]
    clf = clf.fit([eval(t.features) for t in train], [int(t.same) for t in train])

    for ln in Contribution.objects.all().values('last_name').distinct():
        toupdate = []
        for m in Match.objects.filter(c1__last_name=ln['last_name']):
            edge = clf.predict_proba(eval(m.features))
            if edge[0][1] > edge[0][0]:        
                m.classifier_same = True
                m.score = edge[0][1]
            else:
                m.classifier_same = False
                m.score = edge[0][0]
            toupdate.append(m)
        commit_saves(toupdate)
    return

def sample_unmatching(n=500):
    outfile = open('outputs/errorsample.txt', 'a')
    outfile.write('C1|C2|CRP_SAME|CLASSIFIER_SAME|SCORE\n')
    for m in Match.objects.exclude(classifier_same=F('same')).order_by('?')[:n]:
        outfile.write('%s|%s|%s|%s|%s\n' % (m.c1_string, m.c2_string, m.same, m.classifier_same, m.score))
    print 'Sample created! See outputs/errorsample.txt'
    return

########## MAIN ##########

if __name__ == '__main__':
    if LOAD: load_data()
    #sample_unmatching()


