import sys, hashlib
import networkx as nx
from networkx.algorithms.components.connected import connected_components
from django.db import connection, transaction
from sklearn.tree import DecisionTreeClassifier
from apps.data.models import Match, Contribution

########## GLOBALS ##########

LOAD = True

TRAINING_DATA = Match.objects.all().order_by('?')[:5000]

########## HELPER FUNCTIONS ##########

@transaction.commit_manually
def commit_saves(tosave_list):
    for item in tosave_list:
        item.save()
    transaction.commit()
    return

def get_match_status(m):
    if m.same == True and m.classifier_same == True:
        return 'TP'
    elif m.same == False and m.classifier_same == False:
        return 'TN'
    elif m.same == True and m.classifier_same == False:
        return 'FN'
    elif m.same == False and m.classifier_same == True:
        return 'FP'
    return None

########## ASSIGNMENT STEPS ##########

def mark_matches():
    ''' 
    These functions assume that we're using the last name grouping method from previous step.
    '''
    clf = DecisionTreeClassifier(compute_importances=True)
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

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
            m.match_status = get_match_status(m)
            toupdate.append(m)
        commit_saves(toupdate)
    return


def assign_clusters():
    clf = DecisionTreeClassifier(compute_importances=True)
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

    print 'Processing last name groups ...'
    for ln in Contribution.objects.all().values('last_name').distinct():
        if not ln['last_name']: continue
        toupdate = []
        G = nx.Graph()
        nameid = hashlib.sha224(ln['last_name']).hexdigest()
        for m in Match.objects.filter(c1__last_name=ln['last_name']):
            edge = clf.predict_proba(eval(m.features))
            if edge[0][1] > edge[0][0]:    
                G.add_edge(m.c1, m.c2)

        ccs = connected_components(G)
        for c in enumerate(ccs):
            donor_id = c[0]
            for i in c[1]:
                classifier_id = '%s%s' % (donor_id, nameid)
                i.classifier_id = classifier_id[:12]
                toupdate.append(i)
        commit_saves(toupdate)

    print 'Cleaning up the leftovers ...'
    tocleanup = []
    for record in Contribution.objects.filter(classifier_id__isnull=True):
        if not record.match_repr: continue
        classifier_id = '99%s' % hashlib.sha224(record.match_repr).hexdigest()
        record.classifier_id = classifier_id[:12]
        tocleanup.append(record)
    commit_saves(tocleanup)
    return

########## MAIN ##########

if __name__ == '__main__':
    mark_matches()