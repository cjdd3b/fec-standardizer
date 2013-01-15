import re, string
from django.db import models

class Contribution(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    transaction_id = models.CharField(max_length=96, blank=True, null=True)
    recipient = models.CharField(max_length=255, blank=True)
    contributor_name = models.CharField(max_length=600, blank=True, db_index=True)
    city = models.CharField(max_length=90, blank=True, db_index=True)
    state = models.CharField(max_length=6, blank=True, db_index=True)
    zip = models.CharField(max_length=27, blank=True, db_index=True)
    employer = models.CharField(max_length=114, blank=True, db_index=True)
    occupation = models.CharField(max_length=114, blank=True, db_index=True)
    date = models.CharField(max_length=24, blank=True)
    amount = models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)
    honorific = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    nick = models.CharField(max_length=255, blank=True, null=True)
    donor_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    def __unicode__(self):
        return '%s: %s' % (self.contributor_name, self.amount)

    @property
    def match_repr(self):
        return '%s %s %s %s %s %s' % (self.contributor_name, self.city, self.state, self.zip, self.occupation, self.employer)


class DemoMatch(models.Model):
    c1 = models.ForeignKey(Contribution, related_name='c1_test', db_index=True)
    c2 = models.ForeignKey(Contribution, related_name='c2_test', db_index=True)
    features = models.CharField(max_length=255)
    same = models.NullBooleanField()
    score = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'Demo Match'
        verbose_name_plural = 'Demo Matches'

    def __unicode__(self):
        return '%s -> %s' % (self.c1, self.c2)

    def c1_string(self):
        return self.c1.match_repr

    def c2_string(self):
        return self.c2.match_repr