# Encoding: utf8
# Copyright 2010 Amaç Herdağdelen
# Original here: https://github.com/amacinho/Name-Gender-Guesser/

import os
MALE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/us_census_1990_males.txt')
FEMALE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/us_census_1990_females.txt')

class NameGender():
    """This class helps to handle two dictionaries which contain the gender
    association scores of names. Provide the gender scores and call
    get_gender_scores to get normalized scores for a name for both genders."""
    def __init__(self, male_file_name=MALE_FILE, female_file_name=FEMALE_FILE):
        """Needs two dictionaries called males and females which contain
        names as keys and their scores. Scores can be in any scale as long
        as they are consistent across male & female
        and non-negative."""
        self.males = self._load_dict(male_file_name)
        self.females = self._load_dict(female_file_name)

    def _load_dict(self, file_name):
        data = dict()
        for line in open(file_name):
            t = line.strip().split("\t")
            if len(t) == 2:
                name = t[0].lower()
                score = float(t[1])
                data[name] = score
        return data

    def _get_raw_male_score(self, name):
        return self.males.get(name, -1.0)

    def _get_raw_female_score(self, name):
        return self.females.get(name, -1.0)

    def get_gender_scores(self, name):
        """ Returns a  tuple (male_score,female_score). If the name
        is not associated with either genders, returns (-1,-1). A return value
        of (1,0) and (0,1) indicates match for only male and female
        respectively"""
        m = self._get_raw_male_score(name)
        f = self._get_raw_female_score(name)
        if m > 0 and f < 0: # Associated with only male
            return (1,0)
        elif m < 0 and f > 0: # Associated with only female
            return (0,1)
        elif m > 0 and f > 0: # Associated with both genders
            tot = m + f
            return (m/tot,f/tot)
        else: # Unknown name
            return (-1,-1)
