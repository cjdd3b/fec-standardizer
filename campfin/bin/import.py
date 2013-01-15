import csv, datetime
from name_cleaver import IndividualNameCleaver
from apps.data.models import *

########## CONSTANTS ##########

DEFAULT_FIELDS = {
    'id': {'message': 'Contribution ID field (default is "id")', 'fieldname': 'id', 'order': 1},
    'transaction_id': {'message': 'Transaction ID field (default is "transaction_id")', 'fieldname': 'transaction_id', 'order': 2},
    'recipient': {'message': 'Recipient field (default is "recipient_name")', 'fieldname': 'recipient_name', 'order': 3},
    'contributor_name': {'message': 'Contributor name field (default is "contributor_name")', 'fieldname': 'contributor_name', 'order': 4},
    'city': {'message': 'City field (default is "contributor_city")', 'fieldname': 'contributor_city', 'order': 5},
    'state': {'message': 'State field (default is "contributor_state")', 'fieldname': 'contributor_state', 'order': 6},
    'zip': {'message': 'ZIP field (default is "contributor_zipcode")', 'fieldname': 'contributor_zipcode', 'order': 7},
    'employer': {'message': 'Employer field (default is "contributor_employer")', 'fieldname': 'contributor_employer', 'order': 8},
    'occupation': {'message': 'Occupation field (default is "contributor_occupation")', 'fieldname': 'contributor_occupation', 'order': 9},
    'date': {'message': 'Date field (default is "date")', 'fieldname': 'date', 'order': 10},
    'amount': {'message': 'Contribution amount field (default is "amount")', 'fieldname': 'amount', 'order': 11},
    'donor_id': {'message': 'Donor ID field (default is "contributor_ext_id")', 'fieldname': 'contributor_ext_id', 'order': 12},
}

########## HELPER FUNCTIONS ##########

def create_records(records):
    '''
    Helper function to bulk create records.
    '''
    Contribution.objects.bulk_create(records)
    return

########## MAIN ##########

print 'Loading contribution records (this might take a while) ...'
raw_data = csv.DictReader(open('../data/crp_slice.csv', 'rU'), delimiter=',', quotechar='"')

for field in sorted(DEFAULT_FIELDS, key=lambda key: DEFAULT_FIELDS[key]['order']):
    input = raw_input(DEFAULT_FIELDS[field]['message'] + ': ')
    if not input == '':
        DEFAULT_FIELDS[field]['fieldname'] = input
    if input == 'NA':
        DEFAULT_FIELDS[field]['fieldname'] = None

i = 0 # Loop counter to trigger bulk saves
bulk_records = []
while True:
    # Manually iterate and be sure to save on final iteration
    try:
        row = raw_data.next()
    except StopIteration: # This is thrown once the iterator is empty, which triggers save on last item
        create_records(bulk_records)
        print '%s records created ...' % i + 1
        break # Be sure to break the loop. This is is the exit condition.

    id = row[DEFAULT_FIELDS['id']['fieldname']]
    created = False
    try: # Manual step-through of get_or_create sans the commit
        record = Contribution.objects.get(id=id)
    except Contribution.DoesNotExist:
        record = Contribution()
        created = True

    for field in DEFAULT_FIELDS.keys():
        setattr(record, field, row[DEFAULT_FIELDS[field]['fieldname']])

    parsed_name = IndividualNameCleaver(record.contributor_name).parse()

    if created and parsed_name:
        record.honorific = parsed_name.honorific
        record.first_name = parsed_name.first
        record.middle_name = parsed_name.middle
        record.last_name = parsed_name.last
        record.suffix = parsed_name.suffix
        record.nick = parsed_name.nick
        
    bulk_records.append(record)
    if i % 5000 == 0:
        create_records(bulk_records)
        print '%s records created ...' % i 
        bulk_records = []

    i += 1 # Increment

print 'Thanks for your patience! Records imported successfully!'