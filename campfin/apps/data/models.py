import re, string
from django.db import models

class Group(models.Model):
    '''
    Groups for the initial processing stage. In practice, these usually correspond
    with last names. But using a group model like this also allows the contributions
    to be grouped based on other critiera. Probably wouldn't be used in an actual live
    application.
    '''
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Contribution(models.Model):
    '''
    Model representing individual contribution records. Basically the equivalent of abbreviated
    raw campaign finance dataset from CRP and Sunlight:
    '''
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
    group = models.ForeignKey(Group, blank=True, null=True, db_index=True)
    donor_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    classifier_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    def __unicode__(self):
        return '%s: %s' % (self.contributor_name, self.amount)

    @property
    def match_repr(self):
        '''
        Representation of a campaign finance record for use in match admin.
        '''
        return '%s %s %s %s %s %s' % (self.contributor_name, self.city, self.state, self.zip, self.occupation, self.employer)


class Match(models.Model):
    '''
    Pairs of contributions that the classifier uses to make its judgments.
    '''
    c1 = models.ForeignKey(Contribution, related_name='c1_set', db_index=True)
    c2 = models.ForeignKey(Contribution, related_name='c2_set', db_index=True)
    features = models.CharField(max_length=255)
    same = models.NullBooleanField()
    classifier_same = models.NullBooleanField()
    score = models.FloatField(blank=True, null=True)
    match_status = models.CharField(max_length=2,
        choices=(('TP', 'True Positive'), ('TN', 'True Negative'), ('FP', 'False Positive'), ('FN', 'False Negative')),
        blank=True, null=True)

    class Meta:
        verbose_name = 'Demo Match'
        verbose_name_plural = 'Demo Matches'

    def __unicode__(self):
        return '%s -> %s' % (self.c1, self.c2)