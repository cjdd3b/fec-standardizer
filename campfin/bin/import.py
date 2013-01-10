import csv, datetime
from name_cleaver import IndividualNameCleaver
from apps.fec.models import *

########## HELPER FUNCTIONS ##########

def create_records(records):
    '''
    Helper function to bulk create records.
    '''
    Contribution.objects.bulk_create(records)
    return

########## MAIN ##########

print 'Loading contribution records (this might take a while) ...'
raw_data = csv.DictReader(open('data/fec_nicar_slice.csv', 'rU'), delimiter=',', quotechar='"')

i = 0 # Loop counter to trigger bulk saves
bulk_records = []
while True:
    # Manually iterate and be sure to save on final iteration
    try:
        row = raw_data.next()
    except StopIteration: # This is thrown once the iterator is empty, which triggers save on last item
        create_records(bulk_records)
        print '%s records created ...' % i
        break # Be sure to break the loop. This is is the exit condition.

    nicarid = row['nicarid']
    created = False
    try: # Manual step-through of get_or_create sans the commit
        record = Contribution.objects.get(nicarid=nicarid)
    except Contribution.DoesNotExist:
        record = Contribution()
        created = True

    for field in row.keys():
        # Get the field from the model so we can retrieve its attributes (such as null)
        modelfield = Contribution._meta.get_field(field)
        data_element = row[field]
        # Deals with special cases where blank values being fed into null fields makes
        # Postgres throw a fit.
        if modelfield.null == True:
            if data_element == '':
                data_element = None
        if field == 'nicar_date':
            if data_element == '00/00/0000':
                data_element = None
            else:
                data_element = datetime.datetime.strptime(data_element, '%m/%d/%Y').strftime('%Y-%m-%d')
        record.__dict__[field] = data_element

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