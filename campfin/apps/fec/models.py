import re, string
from django.db import models

class Contribution(models.Model):
    nicarid = models.IntegerField(primary_key=True, db_index=True)
    filer_id = models.CharField(max_length=27, blank=True)
    amendment_indicator = models.CharField(max_length=3, blank=True)
    report_type = models.CharField(max_length=9, blank=True)
    primgen = models.CharField(max_length=15, blank=True)
    microfilm = models.CharField(max_length=33, blank=True)
    transaction_type = models.CharField(max_length=9, blank=True)
    entity_type = models.CharField(max_length=9, blank=True)
    contributor_name = models.CharField(max_length=600, blank=True, db_index=True)
    nicar_last_name = models.CharField(max_length=600, blank=True)
    nicar_first_name = models.CharField(max_length=600, blank=True)
    city = models.CharField(max_length=90, blank=True, db_index=True)
    state = models.CharField(max_length=6, blank=True, db_index=True)
    zip = models.CharField(max_length=27, blank=True, db_index=True)
    employer = models.CharField(max_length=114, blank=True, db_index=True)
    occupation = models.CharField(max_length=114, blank=True, db_index=True)
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
    honorific = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    nick = models.CharField(max_length=255, blank=True, null=True)
    donor_id = models.IntegerField(null=True)
    
    class Meta:
        db_table = u'fec_contribution'

    def __unicode__(self):
        return '%s: %s' % (self.contributor_name, self.amount)

    @property
    def match_repr(self):
        return '%s %s %s %s %s %s' % (self.contributor_name, self.city, self.state, self.zip, self.occupation, self.employer)


class Match(models.Model):
    c1 = models.ForeignKey(Contribution, related_name='c1', db_index=True)
    c2 = models.ForeignKey(Contribution, related_name='c2', db_index=True)
    features = models.CharField(max_length=255)
    same = models.NullBooleanField()
    for_training = models.BooleanField()
    score = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Matches'

    def __unicode__(self):
        return '%s -> %s' % (self.c1, self.c2)

    def c1_string(self):
        return self.c1.match_repr

    def c2_string(self):
        return self.c2.match_repr