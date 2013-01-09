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
    city = models.CharField(max_length=90, blank=True, null=True)
    state = models.CharField(max_length=6, blank=True, null=True)
    zip = models.CharField(max_length=27, blank=True, null=True)
    employer = models.CharField(max_length=114, blank=True, null=True)
    occupation = models.CharField(max_length=114, blank=True, null=True)
    honorific = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    nick = models.CharField(max_length=255, blank=True, null=True)
    group = models.ForeignKey('Group', null=True)

    def __unicode__(self):
        return self.contributor_name

    def attributes(self):
        return ' '.join([str(getattr(self, field.name)) for field in self._meta.fields[1:12]])

    @property
    def nick_first(self):
        if self.nick:
            return nick
        return self.first_name

    @property
    def clean_name(self):
        name = '%s %s %s %s' % (self.nick_first, self.middle_name, self.last_name, self.suffix)
        name = name.replace(' None', '')
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return ' '.join(regex.sub('', name).lower().split())

    @property
    def clean_first(self):
        name = '%s %s %s' % (self.nick_first, self.middle_name, self.suffix)
        name = name.replace(' None', '')
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return ' '.join(regex.sub('', name).lower().split())


class Group(models.Model):
    label = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.label


class Match(models.Model):
    i1 = models.ForeignKey(Individual, related_name='i1')
    i2 = models.ForeignKey(Individual, related_name='i2')
    features = models.CharField(max_length=255)
    same = models.NullBooleanField()
    for_training = models.BooleanField()
    score = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return '%s -> %s' % (self.i1, self.i2)

    def i1_test(self):
        return self.i1.attributes()

    def i2_test(self):
        return self.i2.attributes()