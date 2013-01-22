from django.db import connection
from apps.data.models import Match, Contribution

########## HELPER FUNCTIONS ##########

def get_field_names(delimiter='|'):
    table_name = Contribution._meta.db_table
    cursor = connection.cursor()
    cursor.execute('''
        SELECT COLUMN_NAME FROM information_schema.columns
        WHERE table_name = '%s' ''' % table_name)
    return delimiter.join([i[0] for i in cursor.fetchall()])

########## TESTS ##########

def potential_fn_contribs():
    outfile = open('outputs/potential_fn_contribs.csv', 'a')
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
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return

def potential_fp_contribs():
    outfile = open('outputs/potential_fp_contribs.csv', 'a')
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
    for row in cursor.fetchall():
        outfile.write('|'.join([str(i) for i in row]) + '\n')
    return


if __name__ == '__main__':
    potential_fp_contribs()
    potential_fn_contribs()