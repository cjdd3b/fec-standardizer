import itertools
from sklearn import tree
from numpy import array
from apps.fec.models import *

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


########## HELPER FUNCTIONS ###########

def shingle(word, n):
    '''
    Not using a generator here, unlike the initial implementation,
    both because it doesn't save a ton of memory in this use case
    and because it was borking the creation of minhashes.
    '''
    return set([word[i:i + n] for i in range(len(word) - n + 1)])

def jaccard_sim(X, Y):
    """Jaccard similarity between two sets"""
    if not X or not Y: return 0
    x = set(X)
    y = set(Y)
    return float(len(x & y)) / len(x | y)


########## FEATURES ##########

def same_last_name(i1, i2):
    match = 0
    if i1.last_name == i2.last_name:
        match = 1
    return match

def same_first_initial(i1, i2):
    match = 0
    if len(i1.first_name) == 0 or len(i2.first_name) == 0: return match
    if i1.first_name[0] == i2.first_name[0]:
        match = 1
    return match

def same_middle_initial(i1, i2):
    match = 0
    if not i1.middle_name or not i2.middle_name:
        return match
    if i1.middle_name[0] == i2.middle_name[0]:
        match = 1
    return match

def one_letter_first_name(i1, i2):
    match = 0
    if len(i1.first_name) == 0 or len(i2.first_name):
        match = 1
    return match

def same_state(i1, i2):
    match = 0
    if not i1.state or i2.state: return match
    if i1.state == i2.state:
        match = 1
    return match

def same_city(i1, i2):
    match = 0
    if not i1.city or i2.city: return match
    if i1.city == i2.city:
        match = 1
    return match

def zip_sim(i1, i2):
    counter = 0
    if len(i1.zip) < 5 or len(i2.zip) < 5: return counter
    for i in range(5):
        if i1.zip[i] == i2.zip[i]:
            counter += 1
        else:
            break
        i += 1
    return counter

def first_name_similarity(i1, i2):
    name1_shingles = shingle(i1.first_name, 2)
    name2_shingles = shingle(i2.first_name, 2)
    return jaccard_sim(name1_shingles, name2_shingles)

def last_name_similarity(i1, i2):
    name1_shingles = shingle(i1.last_name, 2)
    name2_shingles = shingle(i2.last_name, 2)
    return jaccard_sim(name1_shingles, name2_shingles)

def occupation_similarity(i1, i2):
    o1_shingles = shingle(i1.occupation, 3)
    o2_shingles = shingle(i2.occupation, 3)
    return jaccard_sim(o1_shingles, o2_shingles)

def employer_similarity(i1, i2):
    e1_shingles = shingle(i1.employer, 3)
    e2_shingles = shingle(i2.employer, 3)
    return jaccard_sim(e1_shingles, e2_shingles)

# to add:
# distance between zips
# matching industry code
# middle name = first name?
# middle initial = first name?
# gender
# last name similarity
# nonzero features

########## CREATE FEATURE VECTOR #########

def create_featurevector(i1, i2):
    g = globals().copy()
    features = []
    for f in g.values():
        if hasattr(f, 'func_name'):
            if f.func_name in ACTIVE_FEATURES:
                features.append(f(i1, i2))
    return features


########## MAIN ##########

if __name__ == '__main__':

    for group in Group.objects.all():
        individuals = group.individual_set.all()
        tocreate = []
        for c in itertools.combinations(group.individual_set.all(), 2):
            compstring1 = '%s %s %s' % (c[0].clean_first, c[0].city, c[0].state)
            compstring2 = '%s %s %s' % (c[1].clean_first, c[1].city, c[1].state)
            # TODO: Is the 0.1 cutoff alright, or is it losing things? Have to check this out.
            # can it move up or down?
            if jaccard_sim(shingle(compstring1, 2), shingle(compstring2, 2)) > 0.1:
                featurevector = str(create_featurevector(c[0], c[1]))
                # TODO: Need initial match score here for training purposes? Would have to add
                # to model as well.
                m = Match(i1=c[0], i2=c[1], features=featurevector)
                tocreate.append(m)
        Match.objects.bulk_create(tocreate) # TODO: Make this update-friendly