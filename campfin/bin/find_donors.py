import sys, hashlib
import networkx as nx
from django.db import connection, transaction
from networkx.algorithms.components.connected import connected_components
from sklearn.ensemble import RandomForestClassifier
from django.db.models import F
from apps.data.models import Match, Contribution
from utils.db import commit_saves

########## GLOBALS ##########

LOAD = True

TRAINING_DATA = Match.objects.all().order_by('?')[:10000]

########## HELPER FUNCTIONS ##########

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
    clf = RandomForestClassifier(n_estimators=10, random_state=0)
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

    for g in Contribution.objects.all().values('group_id').distinct():
        toupdate = []
        for m in Match.objects.filter(c1__group_id=g['group_id']):
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
    clf = RandomForestClassifier(n_estimators=10, random_state=0)
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

    print 'Processing groups ...'
    for g in Contribution.objects.all().values('group_id').distinct():
        if not g['group_id']: continue
        toupdate = []
        G = nx.Graph()
        nameid = hashlib.sha224(str(g['group_id'])).hexdigest()
        for m in Match.objects.filter(c1__group_id=g['group_id']):
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
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE data_contribution
        set classifier_id = LOWER(SUBSTR(PASSWORD(CONCAT(contributor_name, city, state, zip, employer, occupation)), 2, 12))
        WHERE classifier_id IS null''')
    transaction.commit_unless_managed()
    return

########## MAIN ##########

if __name__ == '__main__':
    #mark_matches()
    assign_clusters()