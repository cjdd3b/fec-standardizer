import numpy as np
from sklearn.cross_validation import KFold
from sklearn import metrics
from apps.data.models import DemoMatch
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

########## GLOBALS ###########

NUMBER_OF_FOLDS = 10

DATASET_SIZE = 20000

RAW_DATA = DemoMatch.objects.all().order_by('?')[:DATASET_SIZE]

FEATURE_VECTORS = np.array([eval(t.features) for t in RAW_DATA])

CORRECT_ANSWERS = np.array([int(t.same) for t in RAW_DATA])

########## TEST FUNCTIONS ##########

def get_f1_for_classifier(classifier):
    kf = KFold(len(CORRECT_ANSWERS), k=NUMBER_OF_FOLDS, indices=False)
    for train, test in kf:
        X_train, X_test, y_train, y_test = FEATURE_VECTORS[train], FEATURE_VECTORS[test], CORRECT_ANSWERS[train], CORRECT_ANSWERS[test]

        # Train and fit SVM classifier
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)

        # Compute and display precision, recall and F1 for each fold
        print metrics.classification_report(y_test, y_pred, target_names=['Nonmatches', 'Matches'])
    return


if __name__ == '__main__':
    #print '---------- SUPPORT VECTOR MACHINE -----------'
    #svm_classifier = svm.SVC(kernel='linear', C=1)
    #get_f1_for_classifier(svm_classifier)

    print '----------- DECISION TREE -----------'
    dtree_classifier = DecisionTreeClassifier(compute_importances=True)
    get_f1_for_classifier(dtree_classifier)

    print '---------- GAUSSIAN NAIVE BAYES -----------'
    gnb_classifier = GaussianNB()
    get_f1_for_classifier(gnb_classifier)

