'''
find_donors.py

This script does two things, which correspond to the documentation here:

https://github.com/cjdd3b/fec-standardizer/wiki/Matching-donors
https://github.com/cjdd3b/fec-standardizer/wiki/Defining-donor-clusters

Now that all potential matching pairs of similar contributions have been generated in preprocessing.py,
this script first goes through each of the pairs and, using a Random Forest classifier, determines
whether they are from the same donor.

If they are from the same donor, the script adds them into a graph structure and connects them together.
It then uses a connected components algorithm, also described in the links above, to find donors so they
can be labeled with unique IDs.
'''

import sys, hashlib
import networkx as nx
from django.db import connection, transaction
from networkx.algorithms.components.connected import connected_components
from sklearn.ensemble import RandomForestClassifier
from django.db.models import F
from apps.data.models import Match, Contribution
from utils.db import commit_saves

########## GLOBALS ##########

# Use a random subset of 10,000 records to train our classifier. Ideally the training set would be
# completely held out from the test set, but we've thoroughly done that testing in tests/classifier_diagnostics.py.

TRAINING_DATA = Match.objects.all().order_by('?')[:10000]

########## HELPER FUNCTIONS ##########

def get_match_status(m):
    '''
    A helper function that labels the nature of the actual ground-truth CRP match status
    vs. the match status returned by the classifier. Basically a way of labeling things the
    classifier got right and wrong. Used in mark_matches below.
    '''
    if m.same == True and m.classifier_same == True:
        return 'TP' # True positive
    elif m.same == False and m.classifier_same == False:
        return 'TN' # True negative
    elif m.same == True and m.classifier_same == False:
        return 'FN' # False negative
    elif m.same == False and m.classifier_same == True:
        return 'FP' # False positive
    return None

########## ASSIGNMENT STEPS ##########

def mark_matches():
    ''' 
    This function is mostly just here for testing whether the classifier and CRP agree at the match
    level. It doesn't do anything in terms of grouping donors, unlike the assign_clusters
    function below. You can run it or not -- it doesn't matter.
    '''
    # Prepare our Random Forest classifier and train using the training set above
    clf = RandomForestClassifier(n_estimators=10, random_state=0)
    # Training the Random Forest takes two inputs: a list of feature vectors and a list of correct
    # classifications associated with those vectors. More info here:
    # http://scikit-learn.org/dev/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

    # Loop through each of the initial groups we created
    for g in Contribution.objects.all().values('group_id').distinct():
        toupdate = []
        # Now go through all the contribution pairs within a given group
        for m in Match.objects.filter(c1__group_id=g['group_id']):
            # Use the classifier to predict, based on the match feature vector, whether the donors
            # are the same. This returns a probability score of yes vs. no
            edge = clf.predict_proba(eval(m.features))
            # If the yes probability outweighs the no
            if edge[0][1] > edge[0][0]:
                # Mark them as the same and record confidence score
                m.classifier_same = True
                m.score = edge[0][1]
            else:
                # Or else mark them as a non-match and record the score
                m.classifier_same = False
                m.score = edge[0][0]
            # Now compare our classifier's judgment vs. the ground truth CRP data and mark accordingly
            m.match_status = get_match_status(m)
            toupdate.append(m)
        # Using manual transaction management to speed things up. See utils/db.py
        commit_saves(toupdate)
    return


def assign_clusters():
    '''
    This function does the actual donor assignment, assigning unique donor IDs in the contribution table
    based on clusters of contributions that appear to have the same donor. It works pretty much the same
    as the mark_matches function above.
    '''
    # Again, instantiate and train our classifier
    clf = RandomForestClassifier(n_estimators=10, random_state=0)
    clf = clf.fit([eval(t.features) for t in TRAINING_DATA], [int(t.same) for t in TRAINING_DATA])

    # Loop through the last name groups
    print 'Processing groups ...'
    for g in Contribution.objects.all().values('group_id').distinct():
        if not g['group_id']: continue
        toupdate = []
        G = nx.Graph() # Create an empty network graph for each last name group
        # We're using a simple hash function to help generate unique donor IDs
        nameid = hashlib.sha224(str(g['group_id'])).hexdigest()
        # For each match in a last name group
        for m in Match.objects.filter(c1__group_id=g['group_id']):
            # Do the two contributions have the same donor? Same as above.
            edge = clf.predict_proba(eval(m.features))
            if edge[0][1] > edge[0][0]:
                # If they do, add an edge between those contributions in the network graph we created
                # a few steps ago. This process is outlined in the steps here:
                # https://github.com/cjdd3b/fec-standardizer/wiki/Matching-donors
                G.add_edge(m.c1, m.c2)

        # Now we want to go through the graph we created and basically find all the contributions that are
        # connected. If the contributions were connected in the step above, that means they're probably from
        # the same donor. So a donor is basically defined by small networks of connected contributions. This
        # is described further here: https://github.com/cjdd3b/fec-standardizer/wiki/Defining-donor-clusters
        ccs = connected_components(G)

        # Now loop through each of the donor clusters generated by the connected_components function
        for c in enumerate(ccs):
            donor_id = c[0]
            for i in c[1]:
                # Create a donor ID based on our group hash above and the enumerated cluster number
                classifier_id = '%s%s' % (donor_id, nameid)
                i.classifier_id = classifier_id[:12]
                toupdate.append(i)
        # Bulk save the donor IDs to the contribution table
        commit_saves(toupdate)

    # The above step only labels donors who appear in more than one contribution. This step assigns a unique ID
    # to all the one-time donors that don't appear in the clusters. It's mostly just a cleanup step.
    print 'Cleaning up the leftovers ...'
    cursor = connection.cursor()
    # For ease and speed, we're just using MySQL's password hash function to create a unique ID for each one-time donor.
    # Beats running a loop, which is a lot slower.
    cursor.execute('''
        UPDATE data_contribution
        set classifier_id = LOWER(SUBSTR(PASSWORD(CONCAT(contributor_name, city, state, zip, employer, occupation)), 2, 12))
        WHERE classifier_id IS null''')
    transaction.commit_unless_managed()
    return

########## MAIN ##########

if __name__ == '__main__':
    assign_clusters()

    # Uncomment this if you want to see how classification looks at the match object level.
    # Be warned though -- it takes a while.
    # mark_matches()