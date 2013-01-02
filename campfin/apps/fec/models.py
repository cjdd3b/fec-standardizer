import re, string
from django.db import models

class Contribution(models.Model):
    filer_id = models.CharField(max_length=27, blank=True)
    amendment_indicator = models.CharField(max_length=3, blank=True)
    report_type = models.CharField(max_length=9, blank=True)
    primgen = models.CharField(max_length=15, blank=True)
    microfilm = models.CharField(max_length=33, blank=True)
    transaction_type = models.CharField(max_length=9, blank=True)
    entity_type = models.CharField(max_length=9, blank=True)
    contributor_name = models.CharField(max_length=600, blank=True)
    nicar_last_name = models.CharField(max_length=600, blank=True)
    nicar_first_name = models.CharField(max_length=600, blank=True)
    city = models.CharField(max_length=90, blank=True)
    state = models.CharField(max_length=6, blank=True)
    zip = models.CharField(max_length=27, blank=True)
    employer = models.CharField(max_length=114, blank=True)
    occupation = models.CharField(max_length=114, blank=True)
    trans_date = models.CharField(max_length=24, blank=True)
    nicar_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    other_id = models.CharField(max_length=27, blank=True)
    transaction_id = models.CharField(max_length=96, blank=True)
    file_number = models.CharField(max_length=66, blank=True)
    memo_code = models.CharField(max_length=3, blank=True)
    memo_text = models.CharField(max_length=300, blank=True)
    fec_record = models.CharField(max_length=57, blank=True)
    nicar_election_year = models.CharField(max_length=12, blank=True)
    nicarid = models.IntegerField(primary_key=True)
    
    class Meta:
        db_table = u'fec_contribution'

    def __unicode__(self):
        return '%s: %s' % (self.contributor_name, self.amount)


class Individual(models.Model):
    contributor_name = models.CharField(max_length=600, blank=True)
    city = models.CharField(max_length=90, blank=True)
    state = models.CharField(max_length=6, blank=True)
    zip = models.CharField(max_length=27, blank=True)
    employer = models.CharField(max_length=114, blank=True)
    occupation = models.CharField(max_length=114, blank=True)
    honorific = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    suffix = models.CharField(max_length=20, blank=True)
    nick = models.CharField(max_length=255, blank=True)
    group = models.ForeignKey('Group')

    def __unicode__(self):
        return self.contributor_name

    def scrub(self):
        from name_cleaver import IndividualNameCleaver
        if not self.contributor_name:
            return

        parsed_name = IndividualNameCleaver(self.contributor_name).parse()
        try:
            self.honorific = parsed_name.honorific
            self.first_name = parsed_name.first
            self.middle_name = parsed_name.middle
            self.last_name = parsed_name.last
            self.suffix = parsed_name.suffix
            self.nick = parsed_name.nick
            self.save()
        except:
            print self.contributor_name
        return

    @property
    def clean_name(self):
        name = '%s %s %s %s %s' % (self.first_name, self.middle_name, self.last_name, self.suffix, self.nick)
        regex = re.compile('[%s]|None' % re.escape(string.punctuation))
        return ' '.join(regex.sub('', name).upper().split())


class Group(models.Model):
    label = models.CharField(max_length=255)
    count = models.IntegerField(blank=True, null=True)
