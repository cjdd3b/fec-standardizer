from utils.similarity import jaccard_sim, shingle
from utils.namegender import NameGender

'''
features.py

A list of feature functions used for the models that determine whether two
contributions match. Each function should take as arguments two contribution
objects and return an int or float for the feature vector.

Many of these return a binary 1/0, like same_last_name (returns 1 if the last)
name is the same; 0 otherwise. But others, like first_name_similarity, return
a float representing the Jaccard similarity between two shingled strings.
'''

########## GLOBALS ##########

# Loading once here keeps from having to constantly reload the
# name files for every single comparison. See utils/namegender.py for code info
ng = NameGender()

########## HELPER FUNCTIONS ##########

def clean_str(val):
    '''
    Helper function to lowercase and strip input string.
    '''
    if not val: return ' '
    return val.lower().strip()


########## FEATURES ##########

def same_last_name(c1, c2):
    '''
    Do two contribution donors have identical last names?

    Returns 1 or 0
    '''
    match = 0
    if clean_str(c1.last_name) == clean_str(c2.last_name):
        match = 1
    return match

def same_first_name(c1, c2):
    '''
    Do two contribution donors have identical first names?

    Returns 1 or 0
    '''
    match = 0
    if clean_str(c1.first_name) == clean_str(c2.first_name):
        match = 1
    return match

def same_middle_initial(c1, c2):
    '''
    Do two contribution donors have identical middle initials?

    Returns 1 or 0
    '''
    match = 0
    if clean_str(c1.middle_name)[0] == clean_str(c2.middle_name)[0]:
        match = 1
    return match

def same_state(c1, c2):
    '''
    Do two contribution donors report coming from the same state?

    Returns 1 or 0
    '''
    match = 0
    if clean_str(c1.state) == clean_str(c2.state):
        match = 1
    return match

def same_city(c1, c2):
    '''
    Do two contribution donors report coming from the same city?

    Returns 1 or 0
    '''
    match = 0
    if clean_str(c1.city) == clean_str(c2.city):
        match = 1
    return match

def zip_sim(c1, c2):
    '''
    Starting from the beginning of a ZIP code, how many digits to the ZIP codes of
    two contribution donors share?

    Returns a value of 1-5 normalized by the typical ZIP code length of 5.
    '''
    counter = 0.0
    z1, z2 = clean_str(c1.zip), clean_str(c2.zip)
    if len(z1) < 5 or len(z2) < 5: return counter
    for i in range(5):
        if z1[i] == z2[i]:
            counter += 1
        else:
            break
        i += 1
    return counter / 5.0

def first_name_similarity(c1, c2):
    '''
    How similar are the two contribution donors' first names? Based on jaccard similarity
    of 3-shingles of the names.

    Returns a float between 0 and 1, with 1 being identical.
    '''
    name1_shingles = shingle(clean_str(c1.first_name), 3)
    name2_shingles = shingle(clean_str(c2.first_name), 3)
    return jaccard_sim(name1_shingles, name2_shingles)

def occupation_similarity(c1, c2):
    '''
    How similar are the two contribution donors' occupation strings? Based on jaccard similarity
    of 3-shingles of the names.

    Returns a float between 0 and 1, with 1 being identical.
    '''
    o1_shingles = shingle(clean_str(c1.occupation), 3)
    o2_shingles = shingle(clean_str(c2.occupation), 3)
    return jaccard_sim(o1_shingles, o2_shingles)

def employer_similarity(c1, c2):
    '''
    How similar are the two contribution donors' employer strings? Based on jaccard similarity
    of 3-shingles of the names.

    Returns a float between 0 and 1, with 1 being identical.
    '''
    e1_shingles = shingle(clean_str(c1.employer), 3)
    e2_shingles = shingle(clean_str(c2.employer), 3)
    return jaccard_sim(e1_shingles, e2_shingles)

def contributor_name_similarity(c1, c2):
    '''
    How similar are the two contribution donors' full unprocessed contributor names?
    Based on jaccard similarity of 3-shingles of the names.

    Returns a float between 0 and 1, with 1 being identical.
    '''
    e1_shingles = shingle(clean_str(c1.contributor_name), 3)
    e2_shingles = shingle(clean_str(c2.contributor_name), 3)
    return jaccard_sim(e1_shingles, e2_shingles)

def same_gender(c1, c2):
    '''
    Do the two contribution donors have the same gender? Based on code from utils/namegender.py

    Returns 1 or 0.
    '''
    n1_gender = ng.get_gender_scores(clean_str(c1.first_name))
    n2_gender = ng.get_gender_scores(clean_str(c2.first_name))
    if n1_gender.index(max(n1_gender)) == n2_gender.index(max(n2_gender)):
        return 1
    return 0

def same_zip_region(c1, c2):
    '''
    Do the two contribution donors come from the same ZIP code region?

    More info on ZIP codes here: http://en.wikipedia.org/wiki/ZIP_code

    Returns 1 or 0.
    '''
    if clean_str(c1.zip)[0] == clean_str(c2.zip)[0]:
        return 1
    return 0

def same_zip_sectionalcenter(c1, c2):
    '''
    Do the two contribution donors come from the same ZIP code sectional center?

    More info on ZIP codes here: http://en.wikipedia.org/wiki/ZIP_code

    Returns 1 or 0.
    '''
    if clean_str(c1.zip)[:3] == clean_str(c2.zip)[:3]:
        return 1
    return 0

def same_zip_cityarea(c1, c2):
    '''
    Do the two contribution donors come from the same ZIP code city area?

    More info on ZIP codes here: http://en.wikipedia.org/wiki/ZIP_code

    Returns 1 or 0.
    '''
    if clean_str(c1.zip) == clean_str(c2.zip):
        return 1
    return 0

def same_suffix(c1, c2):
    '''
    Do the two contribution donors share the same suffix? (Jr., Sr., etc.)

    Returns 1 or 0.
    '''
    match = 0
    if clean_str(c1.suffix) == clean_str(c2.suffix):
        match = 1
    return match