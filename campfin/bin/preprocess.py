'''
preprocessing.py

This script actually does a couple of things. First, it divides the raw contribution data into 
smaller groups that are easier to process, as described here: 

https://github.com/cjdd3b/fec-standardizer/wiki/Preprocessing

Then, it splits each group into pairs of contributions that may or may not be from the same donor.
This is at the heart of our graph-based approach to this problem, which is described in detail here:

https://github.com/cjdd3b/fec-standardizer/wiki/Matching-donors
https://github.com/cjdd3b/fec-standardizer/wiki/Defining-donor-clusters

Finally, this script generates a feature vector across 15 pieces of data, such as name and ZIP code
similarity, that can help inform a judgment that two contributions come from the same or different
donors. That process is also described in the links above.
'''

import itertools, random
from apps.data.models import Contribution, Match, Group
from utils.similarity import jaccard_sim, shingle
from utils.lsh.lsh import Cluster
from utils.db import commit_saves
from learn.features import *

########## GLOBALS ##########

# Active features that should go into the feature vector. These correspond to function
# names from learn/features.py. You can comment some of these out if you don't want them
# to be part of the featureset for whatever reason.

ACTIVE_FEATURES = [
    'same_last_name',
    'same_first_name',
    'same_middle_initial',
    'same_state',
    'same_city',
    'zip_sim',
    'first_name_similarity',
    'occupation_similarity',
    'employer_similarity',
    'contributor_name_similarity',
    'same_gender',
    'same_zip_region',
    'same_zip_sectionalcenter',
    'same_zip_cityarea',
    'same_suffix',
]

INITIAL_SIM = 0.1

########## GROUPING FUNCTIONS ##########

def group_by_last_name():
    '''
    Groups all of our contribution data by last name.

    In production, we shouldn't have to keep track of these groups in a database -- we'd just choose
    a grouping function and stick with it. I'm using the database approach here so we can easily switch
    between last names and LSH for testing purposes. But using a generator is much quicker. See example
    here: https://github.com/cjdd3b/fec-standardizer/blob/906f1efaf6df47997da5b7c7e55ccf3b67be95fd/campfin/bin/extract_features.py#L31-L38
    '''
    for c in Contribution.objects.all().values('last_name').distinct():
        g, created = Group.objects.get_or_create(name='NAME: %s' % c['last_name'])
        contribs = Contribution.objects.filter(last_name=c['last_name']).update(group=g)
    return

def group_by_lsh():
    '''
    Groups all of our contribution data by the output of a locality sensitive hashing function. The
    LSH implementation is stored in utils/lsh. You can read more about it here:

    http://en.wikipedia.org/wiki/Locality-sensitive_hashing
    '''
    # First step is to create the actual LSH clusters, based on 1-shingles of the names
    cluster = Cluster(threshold=1.0)
    for ln in Contribution.objects.values('last_name').distinct():
        name = ln['last_name']
        if not name: continue # If last name isn't filled out for some reason
        cluster.add_set(shingle(name, 1), name)

    # Next step is to iterate through those clusters and produce an output of each set
    # of last names, along with the contributions associated with them.
    for c in enumerate(cluster.get_sets()):
        for name in c[1]:
            g, created = Group.objects.get_or_create(name='LSH: %s' % c[0])
            Contribution.objects.filter(last_name=name).update(group=g)
    return

########## CREATE FEATURE VECTOR #########

def create_featurevector(c1, c2):
    '''
    Creates a feature vector for a given pair of contributions.
    '''
    # Loops through all of the globals, which include the functions we imported
    # from learn/features.py
    g = globals().copy()
    features = []
    for f in g.values():
        # All our features are functions
        if hasattr(f, 'func_name'):
            # If the function name is in our active features list from above, add it
            # to the list
            if f.func_name in ACTIVE_FEATURES:
                features.append(f(c1, c2))
    return features # Return

def get_featurevector_order():
    '''
    Basically the same as above, but returns the order of the features as they appear
    in the feature vector. This is a little hacky, but the ordering of the vector is kind
    of confusing, so this helps as a reference.
    '''
    features = []
    g = globals().copy()
    for f in g.values():
        if hasattr(f, 'func_name'):
            if f.func_name in ACTIVE_FEATURES:
                features.append(f.func_name)
    return features

########## MAIN ##########

if __name__ == '__main__':
    # First do the initial groupings
    print 'Forming initial groups ...'
    group_by_last_name() # In this case, we're using the last name function from above

    # Now loop through the groups we just created and start putting together potential matches
    print 'Preprocessing matches ...'
    for g in Group.objects.all():
        tocreate = []
        # For any given last name, split up the contributions into every possible combibation of pairs
        for c in itertools.combinations(g.contribution_set.all(), 2):
            compstring1 = '%s %s %s' % (c[0].first_name, c[0].city, c[0].state)
            compstring2 = '%s %s %s' % (c[1].first_name, c[1].city, c[1].state)
            # Check to see if the two donors in a given pair are even remotely similar. If they're not, ignore.
            if jaccard_sim(shingle(compstring1.lower(), 2), shingle(compstring2.lower(), 2)) >= INITIAL_SIM:
                # But if they are, create a feature vector describing the dimensions of their similarity for the
                # machine learning algorithm to use later.
                c1, c2 = c[0], c[1]
                featurevector = str(create_featurevector(c1, c2))
                # Save that feature vector and other information into a match object
                match = Match(c1=c1, c2=c2, features=featurevector)
                match.same = False
                # If the two contributions in the pair are regarded as coming from the same donor by the ground-truth
                # CRP data, mark them as a match so we can use them for testing and training the classifier.
                if (c1.donor_id and c2.donor_id) and (c1.donor_id == c2.donor_id):
                    match.same = True
                tocreate.append(match)
        # Again, we're bulk creating to cut down on database transactions.
        Match.objects.bulk_create(tocreate)

    print '---------- FEATURE VECTOR ORDER ----------'
    # Print out the feature vector order for future reference.
    print get_featurevector_order()