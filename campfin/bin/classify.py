from sklearn import tree
from numpy import array
from apps.fec.models import *

# last name similarity
# first initial same
# first name similarity
# middle initial same
# middle name same
# same state
# same city
# zip code starts the same
# zip code similarity
# occupation similarity
# employer similarity
# middle name = first name?
# middle initial = first name?

# to add:
# distance between zips
# matching industry code
# pct to dems
# pct to reeps
# General range of contributions. Lots or a few.

#X = [['1', '1', '0.4', 'Y'], ['N', 'Y', 'N', 'N']]
#y = [11, 12]
#clf = tree.DecisionTreeClassifier()
#clf = clf.fit(X, y)
#print clf.predict([['Y', 'Y', 'Y', 'Y']])

def create_featurevector(i, i2):
    vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if i.last_name == i2.last_name:
        vector[0] = 1

    if i.first_name == i2.first_name:
        vector[1] = 1

    if i.middle_name == i2.middle_name:
        vector[2] = 1

    if i.first_name[0] == i2.first_name[0]:
        vector[3] = 1

    if i.middle_name:
        if i.middle_name[0] == i2.middle_name[0]:
            vector[4] = 1

    if i.state == i2.zip:
        vector[5] = 1

    if i.zip == i2.zip:
        vector[6] = 1

    if i.zip[:3] == i2.zip[:3]:
        vector[7] = 1

    print vector

for i in Group.objects.get(pk=23).individual_set.all():
    for i2 in Group.objects.get(pk=23).individual_set.exclude(pk=i.pk):
        create_featurevector(i, i2)
        
