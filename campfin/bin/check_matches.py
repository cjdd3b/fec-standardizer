import sys, hashlib
import networkx as nx
from networkx.algorithms.components.connected import connected_components
from django.db import transaction
from django.db.models import F
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

def get_field_names(delimiter='|'):
    table_name = Contribution._meta.db_table
    cursor = connection.cursor()
    cursor.execute('''
        SELECT COLUMN_NAME FROM information_schema.columns
        WHERE table_name = '%s' ''' % table_name)
    return delimiter.join([i[0] for i in cursor.fetchall()])

########## ASSIGNMENT STEPS ##########

def load_data():
    '''
    These functions assume that we're using the last name method.
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


########## TESTS ##########

def sample_unmatching_pairs(n=500):
    outfile = open('outputs/sample_unmatching_pairs.txt', 'a')
    outfile.write('C1|C2|CRP_SAME|CLASSIFIER_SAME|SCORE\n')
    for m in Match.objects.exclude(classifier_same=F('same')).order_by('?')[:n]:
        outfile.write('%s|%s|%s|%s|%s\n' % (m.c1_string, m.c2_string, m.same, m.classifier_same, m.score))
    print 'Sample created! See outputs/errorsample.txt'
    return

def potential_fn_contribs():
    outfile = open('outputs/potential_fn_contribs.csv', 'a')
    outfile.write(get_field_names() + '\n')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT data_contribution.*
        FROM data_contribution,
        (SELECT donor_id, COUNT(distinct classifier_id) AS c
        FROM data_contribution
        WHERE donor_id <> ''
        GROUP BY donor_id
        HAVING c >= 2
        ORDER BY 2 DESC) counter
        WHERE data_contribution.donor_id = counter.donor_id''')
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return

def potential_fp_contribs():
    outfile = open('outputs/potential_fp_contribs.csv', 'a')
    outfile.write(get_field_names() + '\n')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT data_contribution.*
        FROM data_contribution,
        (SELECT classifier_id, COUNT(distinct donor_id) AS c
        FROM data_contribution
        WHERE donor_id <> ''
        GROUP BY classifier_id
        HAVING c >= 2
        ORDER BY 2 DESC) counter
        WHERE data_contribution.classifier_id = counter.classifier_id''')
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return


########## MAIN ##########

if __name__ == '__main__':
    #if LOAD: load_data()
    #assign_clusters()
    potential_fp_contribs()
    potential_fn_contribs()


