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

DATASET_SIZE = 100000

RAW_DATA = Match.objects.all().order_by('?')[:DATASET_SIZE]

FEATURE_VECTORS = np.array([eval(t.features) for t in RAW_DATA])

CORRECT_ANSWERS = np.array([int(t.same) for t in RAW_DATA])

########## TEST FUNCTIONS ##########

def get_scores_for_classifier(classifier, folds=10, score_func=metrics.f1_score):
    '''
    Returns the average F1 score over a number of folds for
    the input classifier.
    '''
    scores = cross_validation.cross_val_score(classifier, FEATURE_VECTORS, CORRECT_ANSWERS, cv=folds, score_func=score_func)
    return "%s (%s folds): %0.2f (+/- %0.2f)\n" % (score_func.__name__, folds, scores.mean(), scores.std() / 2)

def get_feature_importances(classifier):
    classifier.fit(FEATURE_VECTORS, CORRECT_ANSWERS)
    importances = classifier.feature_importances_
    for f in xrange(len(importances)):
        print "feature %d (%f)" % (f + 1, importances[f])

    std = np.std(importances, axis=0)
    indices = np.argsort(importances)[::-1]

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
    DATASET_SIZE = 20000
    svm_classifier = svm.SVC(kernel='linear', C=1)
    print get_scores_for_classifier(svm_classifier, folds=10, score_func=metrics.precision_score)
    print get_scores_for_classifier(svm_classifier, folds=10, score_func=metrics.recall_score)
    print get_scores_for_classifier(svm_classifier)
    DATASET_SIZE = 100000

    # Get feature importances for the Decision Tree, which is the classifier we ultimately will use
    get_feature_importances(rforest_classifier)