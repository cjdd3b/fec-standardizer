import itertools, random
from apps.data.models import Contribution, Match
from utils.similarity import jaccard_sim, shingle
from utils.lsh.lsh import Cluster
from learn.features import *

########## GLOBALS ##########

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

INITIAL_LIKELIHOOD = 0.1

########## GROUPING FUNCTIONS ##########

def last_names():
    '''
    Should return a list or generator data in this format:
    (group_name, [list, of, Contribution, objects])
    '''
    contribs = Contribution.objects.all().order_by('last_name')
    for group in itertools.groupby(contribs, lambda ln: ln.last_name):
            yield group

def lsh():
    # First step is to create the actual LSH clusters, based on 1-shingles of the names
    cluster = Cluster(threshold=1.0)
    for ln in Contribution.objects.values('last_name').distinct():
        name = ln['last_name']
        if not name: continue # If last name isn't filled out for some reason
        cluster.add_set(shingle(name, 1), name)

    # Next step is to iterate through those clusters and produce an output of each set
    # of last names, along with the contributions associated with them.
    for c in cluster.get_sets():
        for name in c:
            yield (name, Contribution.objects.filter(last_name=name))

########## CREATE FEATURE VECTOR #########

def create_featurevector(c1, c2):
    g = globals().copy()
    features = []
    for f in g.values():
        if hasattr(f, 'func_name'):
            if f.func_name in ACTIVE_FEATURES:
                features.append(f(c1, c2))
    return features

def get_featurevector_order():
    features = []
    g = globals().copy()
    for f in g.values():
        if hasattr(f, 'func_name'):
            if f.func_name in ACTIVE_FEATURES:
                features.append(f.func_name)
    return features

########## MAIN ##########

GROUPING_FUNCTION = last_names()

if __name__ == '__main__':
    for g in GROUPING_FUNCTION:
        tocreate = []
        for c in itertools.combinations(g[1], 2):
            compstring1 = '%s %s %s' % (c[0].first_name, c[0].city, c[0].state)
            compstring2 = '%s %s %s' % (c[1].first_name, c[1].city, c[1].state)
            if jaccard_sim(shingle(compstring1.lower(), 2), shingle(compstring2.lower(), 2)) >= INITIAL_LIKELIHOOD:
                c1, c2 = c[0], c[1]
                featurevector = str(create_featurevector(c1, c2))
                match = Match(c1=c1, c2=c2, features=featurevector)
                match.same = False
                match.active = True
                if (c1.donor_id and c2.donor_id) and (c1.donor_id == c2.donor_id):
                    match.same = True
                tocreate.append(match)
        Match.objects.bulk_create(tocreate)

    print '---------- FEATURE VECTOR ORDER ----------'
    print get_featurevector_order()