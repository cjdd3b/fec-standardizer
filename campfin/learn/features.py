from similarity import jaccard_sim, shingle

'''
features.py

A list of feature functions used for the models that determine whether two
contributions match. Each function should take as arguments two contribution
objects and return an int or float for the feature vector.

Many of these return a binary 1/0, like same_last_name (returns 1 if the last)
name is the same; 0 otherwise. But others, like first_name_similarity, return
a float representing the Jaccard similarity between two shingled strings.
'''

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
# number of nonzero features
# addresses would be huge