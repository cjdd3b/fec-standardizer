import itertools, random
from apps.data.models import Contribution, DemoMatch
from utils.similarity import jaccard_sim, shingle
from learn.features import *

########## GLOBALS ##########

ACTIVE_FEATURES = [
    'same_last_name',
    'same_first_initial',
    'same_middle_initial',
    'same_state',
    'same_city',
    'zip_sim',
    'first_name_similarity',
    'occupation_similarity',
    'employer_similarity',
]

########## GROUPING FUNCTIONS ##########

def last_names():
    '''
    Should return a list or generator data in this format:
    (group_name, [list, of, Contribution, objects])
    '''
    contribs = Contribution.objects.all().order_by('last_name')
    for group in itertools.groupby(contribs, lambda ln: ln.last_name):
            yield group

########## CREATE FEATURE VECTOR #########

def create_featurevector(c1, c2):
    g = globals().copy()
    features = []
    for f in g.values():
        if hasattr(f, 'func_name'):
            if f.func_name in ACTIVE_FEATURES:
                features.append(f(c1, c2))
    return features

########## MAIN ##########

GROUPING_FUNCTION = last_names()

for g in GROUPING_FUNCTION:
    tocreate = []
    for c in itertools.combinations(g[1], 2):
        compstring1 = '%s %s %s' % (c[0].first_name, c[0].city, c[0].state)
        compstring2 = '%s %s %s' % (c[1].first_name, c[1].city, c[1].state)
        if jaccard_sim(shingle(compstring1.lower(), 2), shingle(compstring2.lower(), 2)) > 0.1:
            c1, c2 = c[0], c[1]
            featurevector = str(create_featurevector(c1, c2))
            match = DemoMatch(c1=c1, c2=c2, features=featurevector)
            match.same = False
            match.active = True
            if (c1.donor_id and c2.donor_id) and (c1.donor_id == c2.donor_id):
                match.same = True
            tocreate.append(match)
    DemoMatch.objects.bulk_create(tocreate)