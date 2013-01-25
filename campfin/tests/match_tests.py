'''
match_tests.py

Functions to return false negatives and false positives that our process misclassified,
according to CRP ground truth data.
'''

from django.db import connection
from apps.data.models import Match, Contribution

########## HELPER FUNCTIONS ##########

def get_field_names(delimiter='|'):
    '''
    Returns the field names for the Contribution table in order. Used to write
    headers to output CSVs. Can be retrieved automatically on some databases, but
    just easier to do manually to ensure compatibility.
    '''
    fields = ['id', 'transaction_id', 'recipient', 'contributor_name', 'city', 'state',
        'zip', 'employer', 'occupation', 'date', 'amount', 'honorific', 'first_name',
        'middle_name', 'last_name', 'suffix', 'nick', 'group_id', 'donor_id', 'classifier_id']
    return '|'.join(fields)

########## TESTS ##########

def potential_fn_contribs():
    '''
    Returns potential false negatives returned by our classifier from the contributions table.
    Note that this query returns whole groups of names that contain false negative matches, meaning
    it also returns some correct examples.
    '''
    outfile = open('outputs/potential_fn_contribs.csv', 'a')
    # Write a header row to an output csv
    outfile.write(get_field_names() + '\n')
    cursor = connection.cursor()
    cursor.execute('''
            SELECT DISTINCT data_contribution.*
            FROM data_contribution,
            (SELECT donor_id, COUNT(distinct classifier_id) AS c
            FROM data_contribution
            WHERE donor_id <> ''
            GROUP BY donor_id
            HAVING c >= 2
            ORDER BY 2 DESC) counter
            WHERE data_contribution.donor_id = counter.donor_id''')
    # Write each potential false negative to the output file
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return

def potential_fp_contribs():
    '''
    Returns potential false positives returned by our classifier from the contributions table.
    Note that this query returns whole groups of names that contain false positive matches, meaning
    it also returns some correct examples.
    '''
    outfile = open('outputs/potential_fp_contribs.csv', 'a')
    # Write a header row to an output csv
    outfile.write(get_field_names() + '\n')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT data_contribution.*
        FROM data_contribution,
        (SELECT classifier_id, COUNT(distinct donor_id) AS c
        FROM data_contribution
        WHERE donor_id <> ''
        GROUP BY classifier_id
        HAVING c >= 2
        ORDER BY 2 DESC) counter
        WHERE data_contribution.classifier_id = counter.classifier_id''')
    # Write each potential false positive to the output file
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return


if __name__ == '__main__':
    potential_fp_contribs()
    potential_fn_contribs()