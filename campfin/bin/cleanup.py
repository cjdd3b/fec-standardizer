from name_cleaver import IndividualNameCleaver
from apps.fec.models import *

distinct_names = Contribution.objects.values('contributor_name', 'city', 'state', 'zip', 'employer', 'occupation').distinct()
distinct_name_count = len(distinct_names)

to_save = []
for i in xrange(distinct_name_count):
    n = distinct_names[i]
    if not n['contributor_name']:
        continue

    parsed_name = IndividualNameCleaver(n['contributor_name']).parse()

    # Not using get_or_create here because the lookup takes more time. Might be
    # something that we want to use in the long run, however.
    individual = Individual(
        contributor_name = n['contributor_name'],
        city = n['city'],
        state = n['state'],
        zip = n['zip'],
        employer = n['employer'],
        occupation = n['occupation'],
        )

    individual.honorific = parsed_name.honorific
    individual.first_name = parsed_name.first
    individual.middle_name = parsed_name.middle
    individual.last_name = parsed_name.last
    individual.suffix = parsed_name.suffix
    individual.nick = parsed_name.nick # TODO: This needs to return something useful

    # TODO: Should this not group as last names? Group on last names with some level
    # of similarity instead using LSH? Thinking of cases where in one case someone's
    # name is JONES and another it's hyphenated or split like 'JONES BRENNAN'. Or event
    # last name groups that are markedly similar per shingling/Jaccard.
    group, created = Group.objects.get_or_create(label=parsed_name.last)
    if created: group.save()
    individual.group = group

    to_save.append(individual)

    if len(to_save) % 5000 == 0 or distinct_name_count == i + 1:
        Individual.objects.bulk_create(to_save)
        to_save = []