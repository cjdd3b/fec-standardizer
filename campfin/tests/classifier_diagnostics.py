'''
classifier_diagnostics.py

This script tests a number of different machine classifiers on the task
of identifying contributions that likely come from the same donor. Each
classifier is tested using 10-fold cross-validation using the metrics of
precision, recall and F1. Much more information here:

https://github.com/cjdd3b/fec-standardizer/wiki/Matching-donors
'''

import numpy as np
import pylab as pl
from sklearn.cross_validation import KFold
from sklearn import metrics
from sklearn import cross_validation
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from apps.data.models import Match

########## GLOBALS ###########

DATASET_SIZE = 100000 # Total dataset size

RAW_DATA = Match.objects.all().order_by('?')[:DATASET_SIZE] # Raw Match object data

FEATURE_VECTORS = np.array([eval(t.features) for t in RAW_DATA]) # Feature vectors from those objects

CORRECT_ANSWERS = np.array([int(t.same) for t in RAW_DATA]) # And the correct classifications of those objects, per CRP

########## TEST FUNCTIONS ##########

def get_scores_for_classifier(classifier, folds=10, score_func=metrics.f1_score):
    '''
    Returns the average F1, precision and recall score over a number of folds for
    the input classifier. More documentation here:

    http://scikit-learn.org/0.12/modules/cross_validation.html
    '''
    scores = cross_validation.cross_val_score(classifier, FEATURE_VECTORS, CORRECT_ANSWERS, cv=folds, score_func=score_func)
    return "%s (%s folds): %0.2f (+/- %0.2f)\n" % (score_func.__name__, folds, scores.mean(), scores.std() / 2)

def get_feature_importances(classifier):
    '''
    Returns and graphs the feature importances for a given classifier. In this case,
    we just use it to display the results from our Random Forest.
    '''
    classifier.fit(FEATURE_VECTORS, CORRECT_ANSWERS)
    importances = classifier.feature_importances_
    # Print out feature importance scores for the input classifier
    for f in xrange(len(importances)):
        print "feature %d (%f)" % (f + 1, importances[f])

    std = np.std(importances, axis=0)
    indices = np.argsort(importances)[::-1]

    # Use matplotlib to graph the values
    pl.figure()
    pl.title("Feature importances")
    pl.bar(xrange(len(importances)), importances,
       color="r", yerr=std, align="center")
    pl.xticks(xrange(len(importances)))
    pl.xlim([-1, 15])
    pl.show()

    return

########## MAIN ##########

if __name__ == '__main__':
    # Run precision, recall and F1 tests across 5 different classifiers
    print '----------- DECISION TREE -----------'
    dtree_classifier = DecisionTreeClassifier(compute_importances=True)
    print get_scores_for_classifier(dtree_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(dtree_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(dtree_classifier)

    print '---------- LOGISTIC REGRESSION ----------'
    log_classifier = LogisticRegression(C=1.0, penalty='l2', tol=0.01)
    print get_scores_for_classifier(log_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(log_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(log_classifier)

    print '---------- GAUSSIAN NAIVE BAYES -----------'
    gnb_classifier = GaussianNB()
    print get_scores_for_classifier(gnb_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(gnb_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(gnb_classifier)

    print '---------- RANDOM FOREST ----------'
    rforest_classifier = RandomForestClassifier(n_estimators=10, compute_importances=True, random_state=0)
    print get_scores_for_classifier(rforest_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(rforest_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(rforest_classifier)

    print '---------- SUPPORT VECTOR MACHINE -----------'
    DATASET_SIZE = 20000 # SVMs don't perform well with large amounts of data, so we scale down the dataset size here
    svm_classifier = svm.SVC(kernel='linear', C=1)
    print get_scores_for_classifier(svm_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(svm_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(svm_classifier)
    DATASET_SIZE = 100000 # Then we scale it back up

    # Get feature importances for the Decision Tree, which is the classifier we ultimately will use
    get_feature_importances(rforest_classifier)