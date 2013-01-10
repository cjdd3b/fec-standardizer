import itertools
from apps.fec.models import Contribution, Match

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
    Should return a list or generatordata in this format:
    (group_name, [list, of, Contribution, objects])
    '''
    contribs = Contribution.objects.all().order_by('nicar_last_name')
    for group in itertools.groupby(contribs, lambda ln: ln.nicar_last_name):
            yield group

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

def same_last_name(c1, c2):
    match = 0
    if not c1.last_name or not c2.last_name: return match
    if c1.last_name.lower() == c2.last_name.lower():
        match = 1
    return match

def same_first_initial(c1, c2):
    match = 0
    if not c1.first_name or not c2.first_name: return match
    if c1.first_name[0].lower() == c2.first_name[0].lower():
        match = 1
    return match

def same_middle_initial(c1, c2):
    match = 0
    if not c1.middle_name or not c2.middle_name: return match
    if c1.middle_name[0].lower() == c2.middle_name[0].lower():
        match = 1
    return match

def same_state(c1, c2):
    match = 0
    if not c1.state or c2.state: return match
    if c1.state.upper() == c2.state.upper():
        match = 1
    return match

def same_city(c1, c2):
    match = 0
    if not c1.city or c2.city: return match
    if c1.city.lower() == c2.city.lower():
        match = 1
    return match

def zip_sim(c1, c2):
    counter = 0
    # Only look at the first five digits
    if not c1.zip or not c2.zip: return counter
    if len(c1.zip) < 5 or len(c2.zip) < 5: return counter
    for i in range(5):
        if c1.zip[i] == c2.zip[i]:
            counter += 1
        else:
            break
        i += 1
    return counter

def first_name_similarity(c1, c2):
    if not c1.first_name or not c2.first_name: return 0.0
    name1_shingles = shingle(c1.first_name.lower(), 2)
    name2_shingles = shingle(c2.first_name.lower(), 2)
    return jaccard_sim(name1_shingles, name2_shingles)

def last_name_similarity(c1, c2):
    if not c1.last_name or not c2.last_name: return 0.0
    name1_shingles = shingle(c1.last_name.lower(), 2)
    name2_shingles = shingle(c2.last_name.lower(), 2)
    return jaccard_sim(name1_shingles, name2_shingles)

def occupation_similarity(c1, c2):
    if not c1.occupation or not c2.occupation: return 0.0
    o1_shingles = shingle(c1.occupation.lower(), 3)
    o2_shingles = shingle(c2.occupation.lower(), 3)
    return jaccard_sim(o1_shingles, o2_shingles)

def employer_similarity(c1, c2):
    if not c1.employer or not c2.employer: return 0.0
    e1_shingles = shingle(c1.employer.lower(), 3)
    e2_shingles = shingle(c2.employer.lower(), 3)
    return jaccard_sim(e1_shingles, e2_shingles)

# to add:
# maybe city similarity?
# distance between zips
# matching industry code
# jaccard sim of first + middle rather than just first
# gender
# last name similarity
# number of nonzero features
# addresses would be huge

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
            featurevector = str(create_featurevector(c[0], c[1]))
            m = Match(c1=c[0], c2=c[1], features=featurevector)
            tocreate.append(m)
    Match.objects.bulk_create(tocreate)