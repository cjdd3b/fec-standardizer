'''
similarity.py

A collection of helper functions for calculating similarity between
strings and other objects.
'''

########## HELPER FUNCTIONS ###########

def shingle(word, n):
    '''
    Not using a generator here, unlike the initial implementation,
    both because it doesn't save a ton of memory in this use case
    and because it was borking the creation of minhashes.
    '''
    return set([word[i:i + n] for i in range(len(word) - n + 1)])

def jaccard_sim(X, Y):
    """Jaccard similarity between two sets"""
    if not X or not Y: return 0
    x = set(X)
    y = set(Y)
    return float(len(x & y)) / len(x | y)