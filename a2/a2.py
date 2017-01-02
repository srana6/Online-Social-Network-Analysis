# coding: utf-8

"""
CS579: Assignment 2
In this assignment, you will build a text classifier to determine whether a
movie review is expressing positive or negative sentiment. The data come from
the website IMDB.com.
You'll write code to preprocess the data in different ways (creating different
features), then compare the cross-validation accuracy of each approach. Then,
you'll compute accuracy on a test set and do some analysis of the errors.
The main method takes about 40 seconds for me to run on my laptop. Places to
check for inefficiency include the vectorize function and the
eval_all_combinations function.
Complete the 14 methods below, indicated by TODO.
As usual, completing one method at a time, and debugging with doctests, should
help.
"""
# No imports allowed besides these.
from collections import Counter, defaultdict
from itertools import chain, combinations
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.sparse import csr_matrix
from sklearn.cross_validation import KFold
from sklearn.linear_model import LogisticRegression
import string
import tarfile
import urllib.request
from nltk.featstruct import FeatStruct


def download_data():
    """ Download and unzip data.
    DONE ALREADY.
    """
    url = 'https://www.dropbox.com/s/xk4glpk61q3qrg2/imdb.tgz?dl=1'
    urllib.request.urlretrieve(url, 'imdb.tgz')
    tar = tarfile.open("imdb.tgz")
    tar.extractall()
    tar.close()


def read_data(path):
    """
    Walks all subdirectories of this path and reads all
    the text files and labels.
    DONE ALREADY.
    Params:
      path....path to files
    Returns:
      docs.....list of strings, one per document
      labels...list of ints, 1=positive, 0=negative label.
               Inferred from file path (i.e., if it contains
               'pos', it is 1, else 0)
    """
    fnames = sorted([f for f in glob.glob(os.path.join(path, 'pos', '*.txt'))])
    data = [(1, open(f).readlines()[0]) for f in sorted(fnames)]
    fnames = sorted([f for f in glob.glob(os.path.join(path, 'neg', '*.txt'))])
    data += [(0, open(f).readlines()[0]) for f in sorted(fnames)]
    data = sorted(data, key=lambda x: x[1])
    return np.array([d[1] for d in data]), np.array([d[0] for d in data])


def tokenize(doc, keep_internal_punct=False):
    """
    Tokenize a string.
    The string should be converted to lowercase.
    If keep_internal_punct is False, then return only the alphanumerics (letters, numbers and underscore).
    If keep_internal_punct is True, then also retain punctuation that
    is inside of a word. E.g., in the example below, the token "isn't"
    is maintained when keep_internal_punct=True; otherwise, it is
    split into "isn" and "t" tokens.
    Params:
      doc....a string.
      keep_internal_punct...see above
    Returns:
      a numpy array containing the resulting tokens.
    >>> tokenize("Hi there! Isn't this fun?", keep_internal_punct=False)
    array(['hi', 'there', 'isn', 't', 'this', 'fun'], 
          dtype='<U5')
    >>> tokenize("Hi there! Isn't this fun?", keep_internal_punct=True)
    array(['hi', 'there', "isn't", 'this', 'fun'], 
          dtype='<U5')
    >>> tokenize("??necronomicon?? geträumte sünden.<br>Hi", True)
    array(['necronomicon', 'geträumte', 'sünden.<br>hi'], 
          dtype='<U13')
    """
    ###TODO
    tokenList = []
    
    if keep_internal_punct == True:
        tempList = doc.lower().strip().split()
        exclude = string.punctuation

        i=0
        while i<len(tempList):
            tempWord=tempList[i].rstrip(exclude)
            tempWord=tempWord.lstrip(exclude)
            tokenList.append(tempWord)
            i+=1
            
        numpy_array=np.array(tokenList) 
                    
    elif keep_internal_punct == False:
        numpy_array=np.array(re.sub('\W+', ' ', doc.lower()).split())
        
    return numpy_array
    

def token_features(tokens, feats):
    """
    Add features for each token. The feature name
    is pre-pended with the string "token=".
    Note that the feats dict is modified in place,
    so there is no return value.
    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.
    >>> feats = defaultdict(lambda: 0)
    >>> token_features(['hi', 'there', 'hi'], feats)
    >>> sorted(feats.items())
    [('token=hi', 2), ('token=there', 1)]
    """
    ###TODO
    
    i=0
    while i<len(tokens):
        feats['token='+tokens[i]]+=1
        i+=1    
    pass


def token_pair_features(tokens, feats, k=3):
    """
    Compute features indicating that two words occur near
    each other within a window of size k.
    For example [a, b, c, d] with k=3 will consider the
    windows: [a,b,c], [b,c,d]. In the first window,
    a_b, a_c, and b_c appear; in the second window,
    b_c, c_d, and b_d appear. This example is in the
    doctest below.
    Note that the order of the tokens in the feature name
    matches the order in which they appear in the document.
    (e.g., a__b, not b__a)
    Params:
      tokens....array of token strings from a document.
      feats.....a dict from feature to value
      k.........the window size (3 by default)
    Returns:
      nothing; feats is modified in place.
    >>> feats = defaultdict(lambda: 0)
    >>> token_pair_features(np.array(['a', 'b', 'c', 'd']), feats)
    >>> sorted(feats.items())
    [('token_pair=a__b', 1), ('token_pair=a__c', 1), ('token_pair=b__c', 2), ('token_pair=b__d', 1), ('token_pair=c__d', 1)]
    """
    ###TODO
    win = []
    counter = True
    
    while counter:
        result = tuple(tokens[:k])
        if not result:
            counter = False
            continue
        win.append(result)
        tokens = tokens[1:]
    win = [w for w in win if not (len(w) < k)]
    
    i=0
    while i<len(win):
        tempArray=np.array(win[i])
        for tup in list(combinations(tempArray, 2)):
            suffix = '__'.join(tup)
            keys = 'token_pair=' + suffix
            if 'token_pair=' in keys: 
                try:
                    feats[keys]+=1
                except:
                    feats[keys] = 1
            else:
                keys='token_pair='
        i+=1
    pass

neg_words = set(['bad', 'hate', 'horrible', 'worst', 'boring'])
pos_words = set(['awesome', 'amazing', 'best', 'good', 'great', 'love', 'wonderful'])

def lexicon_features(tokens, feats):
    """
    Add features indicating how many time a token appears that matches either
    the neg_words or pos_words (defined above). The matching should ignore
    case.
    Params:
      tokens...array of token strings from a document.
      feats....dict from feature name to frequency
    Returns:
      nothing; feats is modified in place.
    In this example, 'LOVE' and 'great' match the pos_words,
    and 'boring' matches the neg_words list.
    >>> feats = defaultdict(lambda: 0)
    >>> lexicon_features(np.array(['i', 'LOVE', 'this', 'great', 'boring', 'movie']), feats)
    >>> sorted(feats.items())
    [('neg_words', 1), ('pos_words', 2)]
    """
    ###TODO
    feats['pos_words']=0
    feats['neg_words']=0
    i=0
    while i<len(tokens):
        if tokens[i].lower() in pos_words:
            feats['pos_words']+=1
        if tokens[i].lower() in neg_words:
            feats['neg_words']+=1
        i+=1
    pass

def featurize(tokens, feature_fns):
    """
    Compute all features for a list of tokens from
    a single document.
    Params:
      tokens........array of token strings from a document.
      feature_fns...a list of functions, one per feature
    Returns:
      list of (feature, value) tuples, SORTED alphabetically
      by the feature name.
    >>> feats = featurize(np.array(['i', 'LOVE', 'this', 'great', 'movie']), [token_features, lexicon_features])
    >>> feats
    [('neg_words', 0), ('pos_words', 2), ('token=LOVE', 1), ('token=great', 1), ('token=i', 1), ('token=movie', 1), ('token=this', 1)]
    """
    ###TODO
    list1=[]
    feats=defaultdict(lambda: 0)
    i=0
    while i<len(feature_fns):
        function=feature_fns[i]
        function(tokens,feats)
        i+=1
    for key,val in feats.items():
        list1.append((key,val))
    return sorted(list1, key=lambda x:(x[0]),reverse=False)
    pass


def vectorize(tokens_list, feature_fns, min_freq, vocab=None):
    """
    Given the tokens for a set of documents, create a sparse
    feature matrix, where each row represents a document, and
    each column represents a feature.
    Params:
      tokens_list...a list of lists; each sublist is an
                    array of token strings from a document.
      feature_fns...a list of functions, one per feature
      min_freq......Remove features that do not appear in
                    at least min_freq different documents.
    Returns:
      - a csr_matrix: See https://goo.gl/f5TiF1 for documentation.
      This is a sparse matrix (zero values are not stored).
      - vocab: a dict from feature name to column index. NOTE
      that the columns are sorted alphabetically (so, the feature
      "token=great" is column 0 and "token=horrible" is column 1
      because "great" < "horrible" alphabetically),
    >>> docs = ["Isn't this movie great?", "Horrible, horrible movie"]
    >>> tokens_list = [tokenize(d) for d in docs]
    >>> feature_fns = [token_features]
    >>> X, vocab = vectorize(tokens_list, feature_fns, min_freq=1)
    >>> type(X)
    <class 'scipy.sparse.csr.csr_matrix'>
    >>> X.toarray()
    array([[1, 0, 1, 1, 1, 1],
           [0, 2, 0, 1, 0, 0]], dtype=int64)
    >>> sorted(vocab.items(), key=lambda x: x[1])
    [('token=great', 0), ('token=horrible', 1), ('token=isn', 2), ('token=movie', 3), ('token=t', 4), ('token=this', 5)]
    """
    ###TODO
    #print(tokens_list)
    #row_counter=0
    featureDict=defaultdict(lambda: 0)
    tempDict=defaultdict(lambda: 0)
    columnDict=defaultdict(lambda: 0)
    row=[]
    column=[]
    data = []
    
    def set_feature_dict(tokens_list,feature_fns):
        featureDict=defaultdict(lambda: 0)
        rowCount=0
        i=0
        while i<len(tokens_list):
            temp=tokens_list[i]
            featureDict[rowCount]=featurize(temp,feature_fns)
            rowCount+=1
            i+=1
        return featureDict
        
    def set_temp_dict(featureDict):
        tempDict=defaultdict(lambda: 0)
        for key,val in featureDict.items():
            j=0
            while j<len(val):
                x=val[j]
                tempDict[x[0]]+=1
                j+=1
        return tempDict
    
    #calling above methods    
    featureDict=set_feature_dict(tokens_list,feature_fns)
    tempDict=set_temp_dict(featureDict)
  
    finalDict=defaultdict(lambda: 0)
    
    for key,val in tempDict.items():
        if(val>=min_freq):
            finalDict[key]=val
        else:
            val
    
    finalDictList=sorted(finalDict.items(), key=lambda x:(x[0]))
    counter=0
    colcounter=0
    k=0
    while k<len(finalDictList):
        item=finalDictList[k]
        columnDict[item[0]]=counter
        counter+=1
        k+=1
    if(vocab!=None):
        for key,value in featureDict.items():
            for term in value:
                if(term[0] in vocab):
                    row.append(colcounter)
                    column.append(vocab[term[0]])
                    data.append(term[1])
                else:
                    vocab
            colcounter=colcounter+1
            counter=counter+1
            
    elif(vocab==None):
        for key,val in featureDict.items():
            n=0
            while n<len(val):
                x=val[n]
                if(tempDict[x[0]] >= min_freq):
                    row.append(key)
                    column.append(columnDict[x[0]])
                    data.append(x[1])
                else:
                    min_freq
                n+=1
                
    
    return (csr_matrix((data, (row,column)), dtype='int64'),columnDict)
    pass

def accuracy_score(truth, predicted):
    """ Compute accuracy of predictions.
    DONE ALREADY
    Params:
      truth.......array of true labels (0 or 1)
      predicted...array of predicted labels (0 or 1)
    """
    return len(np.where(truth==predicted)[0]) / len(truth)


def cross_validation_accuracy(clf, X, labels, k):
    """
    Compute the average testing accuracy over k folds of cross-validation. You
    can use sklearn's KFold class here (no random seed, and no shuffling
    needed).
    Params:
      clf......A LogisticRegression classifier.
      X........A csr_matrix of features.
      labels...The true labels for each instance in X
      k........The number of cross-validation folds.
    Returns:
      The average testing accuracy of the classifier
      over each fold of cross-validation.
    """
    ###TODO
    accuracies=[]
    lengthOfLables=len(labels)
    if(lengthOfLables>0):
        kfold = KFold(lengthOfLables, k)
    
    for train_ind, test_ind in kfold:
        clf.fit(X[train_ind], labels[train_ind])
        predictions = clf.predict(X[test_ind])
        accuracyValue=accuracy_score(labels[test_ind], predictions)
        accuracies.append(accuracyValue)
    
    averageTestingAccuracy=np.mean(accuracies)
    return averageTestingAccuracy
    pass

def eval_all_combinations(docs, labels, punct_vals,
                          feature_fns, min_freqs):
    """
    Enumerate all possible classifier settings and compute the
    cross validation accuracy for each setting. We will use this
    to determine which setting has the best accuracy.
    For each setting, construct a LogisticRegression classifier
    and compute its cross-validation accuracy for that setting.
    In addition to looping over possible assignments to
    keep_internal_punct and min_freqs, we will enumerate all
    possible combinations of feature functions. So, if
    feature_fns = [token_features, token_pair_features, lexicon_features],
    then we will consider all 7 combinations of features (see Log.txt
    for more examples).
    Params:
      docs..........The list of original training documents.
      labels........The true labels for each training document (0 or 1)
      punct_vals....List of possible assignments to
                    keep_internal_punct (e.g., [True, False])
      feature_fns...List of possible feature functions to use
      min_freqs.....List of possible min_freq values to use
                    (e.g., [2,5,10])
    Returns:
      A list of dicts, one per combination. Each dict has
      four keys:
      'punct': True or False, the setting of keep_internal_punct
      'features': The list of functions used to compute features.
      'min_freq': The setting of the min_freq parameter.
      'accuracy': The average cross_validation accuracy for this setting, using 5 folds.
      This list should be SORTED in descending order of accuracy.
      This function will take a bit longer to run (~20s for me).
    """
    ###TODO
    
    dictList=[]
    featureFunctionList = []
    tokenTrue=[tokenize(d,True) for d in docs]
    tokenFalse=[tokenize(d) for d in docs]

    for r in range(1, len(feature_fns)+1):
        if (r>0):
            for subset in combinations(feature_fns, r):
                featureFunctionList.append(list(subset))
        elif(r<0):
            r

            
    i=0
    while i<len(featureFunctionList):
        feature=featureFunctionList[i]
        j=0
        while j<len(punct_vals):
            punctuation=punct_vals[j]
            k=0
            while k<len(min_freqs):
                frequency=min_freqs[k]
                settings=defaultdict(lambda: 0)
                settings['min_freq']=frequency
                settings['punct']=punctuation
                settings['features']=feature
                
                if (punctuation==True):
                    X,vocab=vectorize(tokenTrue, feature, frequency)
                elif (punctuation==False):
                    X,vocab=vectorize(tokenFalse, feature, frequency)                    
                settings['accuracy']=cross_validation_accuracy(LogisticRegression(), X, labels, 5)
                dictList.append(settings)
                k+=1
            j+=1
        i+=1
                 
             
        
    
    dictList=sorted(dictList, key=lambda x:-x['accuracy'])
    return dictList
    pass


def plot_sorted_accuracies(results):
    """
    Plot all accuracies from the result of eval_all_combinations
    in ascending order of accuracy.
    Save to "accuracies.png".
    """
    ###TODO
    accuracy=[]
    for item in results:
        for key,val in item.items():
            if(key == 'accuracy'):
                accuracy.append(item[key])
                
    if(len(accuracy)>=0):
        vals = sorted(accuracy)
    else:
        vals
    plt.plot(vals)
    plt.xlabel('Settings')
    plt.ylabel('Accuracy')
    plt.savefig("accuracies.png")   
    pass



def mean_accuracy_per_setting(results):
    """
    To determine how important each model setting is to overall accuracy,
    we'll compute the mean accuracy of all combinations with a particular
    min_freq=2.
    Params:
      results...The output of eval_all_combinations
    Returns:
      A list of (accuracy, setting) tuples, SORTED in
      descending order of accuracy.
    """
    ###TODO
    
    settings=defaultdict(lambda: 0)
    featSet=set()
    
    for rValue in range(0,(len(results))):
        str1="features="
        feature_typ=results[rValue]["features"]        
        for ftr in feature_typ:
            str1=str1+" "+ftr.__name__
        featSet.add(str1)
    
    
    for feature in featSet:
        den=0
        for item in results:
            str2="features="
            for itm in item['features']:
                
                str2 = str2 +" "+itm.__name__
            if(feature==str2):
                settings[feature]+=item["accuracy"]
                den+=1
                
        settings[feature]=settings[feature]/den
        
    settings["punct=True"]=0
    settings["punct=False"]=0
    settings["min_freq=5"]=0
    settings["min_freq=10"]=0
    settings["min_freq=2"]=0
    
    punctTrueList=[]
    punctFalseList=[]
    minfreq2List=[]
    minfreq5List=[]
    minfreq10List=[]
            
    index=len(results)-1
    while (index>-1):
        typevalue=results[index]["punct"]
        freqvalue=results[index]["min_freq"]
        if(typevalue==True):
            settings["punct=True"]+=results[index]["accuracy"]
            try: 
                punctTrueList.append(results[index])
            except:
                print("error")
           
        if(typevalue==False):
            settings["punct=False"]+=results[index]["accuracy"]
            try: 
                punctFalseList.append(results[index])
            except:
                print("error")
            
        if(freqvalue==2):    
            settings["min_freq=2"]+=results[index]["accuracy"]
            try: 
                minfreq2List.append(results[index])
            except:
                print("error")
    
        if(freqvalue==5):    
            settings["min_freq=5"]+=results[index]["accuracy"]
            try: 
                minfreq5List.append(results[index])
            except:
                print("error")
          
        if(freqvalue==10):    
            settings["min_freq=10"]+=results[index]["accuracy"]
            try: 
                minfreq10List.append(results[index])
            except:
                print("error")
          
        index=index-1
    settings["punct=False"]=settings["punct=False"]/len(punctTrueList)
    settings["punct=True"]=settings["punct=True"]/len(punctFalseList)
    settings["min_freq=10"]=settings["min_freq=10"]/len(minfreq2List)
    settings["min_freq=5"]=settings["min_freq=5"]/len(minfreq5List)
    settings["min_freq=2"]=settings["min_freq=2"]/len(minfreq10List)
    
    settings_rev=defaultdict(lambda: 0)
    
    for key,value in settings.items():
        settings_rev[value]=key
    return sorted(settings_rev.items(), key=lambda k: -k[0])   
    
    pass


def fit_best_classifier(docs, labels, best_result):
    """
    Using the best setting from eval_all_combinations,
    re-vectorize all the training data and fit a
    LogisticRegression classifier to all training data.
    (i.e., no cross-validation done here)
    Params:
      docs..........List of training document strings.
      labels........The true labels for each training document (0 or 1)
      best_result...Element of eval_all_combinations
                    with highest accuracy
    Returns:
      clf.....A LogisticRegression classifier fit to all
            training data.
      vocab...The dict from feature name to column index.
    """
    ###TODO
    tempList1=[]
    fFunc = best_result['features']
    frequency = best_result['min_freq']
    punctuation = best_result['punct']
    
    if(punctuation==True):
        tempList1 = [tokenize(d,punctuation) for d in docs]
    elif(punctuation==False):
        tempList1 = [tokenize(d) for d in docs]
    
    if(len(tempList1)>=0):    
        x , vocab = vectorize(tempList1,fFunc,frequency)
    else:
        print(len(tempList1))
    
    clf = LogisticRegression()
    
    clf.fit(x,labels)
    
    return clf, vocab
    
    pass


def top_coefs(clf, label, n, vocab):
    """
    Find the n features with the highest coefficients in
    this classifier for this label.
    See the .coef_ attribute of LogisticRegression.
    Params:
      clf.....LogisticRegression classifier
      label...1 or 0; if 1, return the top coefficients
              for the positive class; else for negative.
      n.......The number of coefficients to return.
      vocab...Dict from feature name to column index.
    Returns:
      List of (feature_name, coefficient) tuples, SORTED
      in descending order of the coefficient for the
      given class label.
    """
    ###TODO
    top_coef_terms=[]
    word_list = np.array([key for key,val in sorted(vocab.items(), key=lambda x:x[1])]) 
    coef = clf.coef_[0]
    if (label==1):
        top_coef_ind = np.argsort(coef)[::-1][:n]
    elif (label!=1):
        top_coef_ind = np.argsort(coef)[:n]    
    
    top_coef_terms=word_list[top_coef_ind]
    
    top_coef = abs(coef[top_coef_ind])
    
    final_result=[x for x in zip(top_coef_terms, top_coef)]
    finalResult=sorted(final_result, key=lambda x:-x[1])
    
    return finalResult
    pass


def parse_test_data(best_result, vocab):
    """
    Using the vocabulary fit to the training data, read
    and vectorize the testing data. Note that vocab should
    be passed to the vectorize function to ensure the feature
    mapping is consistent from training to testing.
    Note: use read_data function defined above to read the
    test data.
    Params:
      best_result...Element of eval_all_combinations
                    with highest accuracy
      vocab.........dict from feature name to column index,
                    built from the training data.
    Returns:
      test_docs.....List of strings, one per testing document,
                    containing the raw.
      test_labels...List of ints, one per testing document,
                    1 for positive, 0 for negative.
      X_test........A csr_matrix representing the features
                    in the test data. Each row is a document,
                    each column is a feature.
    """
    ###TODO
    test_docs,test_labels=read_data(os.path.join('data', 'test'))
    if(best_result["punct"]==True):
        tokenList = [tokenize(d,True) for d in test_docs]
    else:    
        tokenList = [tokenize(d) for d in test_docs]
    X_test,vocab=vectorize(tokenList, best_result['features'], best_result['min_freq'],vocab=vocab)
    return test_docs,test_labels,X_test
    pass


def print_top_misclassified(test_docs, test_labels, X_test, clf, n):
    """
    Print the n testing documents that are misclassified by the
    largest margin. By using the .predict_proba function of
    LogisticRegression <https://goo.gl/4WXbYA>, we can get the
    predicted probabilities of each class for each instance.
    We will first identify all incorrectly classified documents,
    then sort them in descending order of the predicted probability
    for the incorrect class.
    E.g., if document i is misclassified as positive, we will
    consider the probability of the positive class when sorting.
    Params:
      test_docs.....List of strings, one per test document
      test_labels...Array of true testing labels
      X_test........csr_matrix for test data
      clf...........LogisticRegression classifier fit on all training
                    data.
      n.............The number of documents to print.
    Returns:
      Nothing; see Log.txt for example printed output.
    """
    ###TODO
    predictedLabels = clf.predict(X_test)
    probabLabels = clf.predict_proba(X_test)
    dictlist = []
   
    i=0
    while i<len(test_docs):
        dictvalues = defaultdict(lambda:0)
        if(predictedLabels[i] != test_labels[i]):
            dictvalues.update(filename= test_docs[i])
            dictvalues.update(index= i)
            dictvalues.update(predicted= predictedLabels[i])
            dictvalues.update(probas= probabLabels[i])
            dictvalues.update(truth= test_labels[i])
            dictlist.append(dictvalues)

        else:
            dictlist
        
        i+=1
        
            
    dict_list = sorted(dictlist, key=lambda x: x['probas'][0] if x['predicted']==0 
                       else x['probas'][1], reverse = True)[:n]
    for value in dict_list:
        if(value['truth']==0):
            print("truth=",value['truth'],"predicted=",value['predicted'],"proba=",value['probas'][1])
            print(value['filename'])
        elif(value['truth']==1):
            print("truth=",value['truth'],"predicted=",value['predicted'],"proba=",value['probas'][0])
            print(value['filename'])
    pass


def main():
    """
    Put it all together.
    ALREADY DONE.
    """
    feature_fns = [token_features, token_pair_features, lexicon_features]
    # Download and read data.
    #download_data()
    docs, labels = read_data(os.path.join('data', 'train'))
    # Evaluate accuracy of many combinations
    # of tokenization/featurization.
    results = eval_all_combinations(docs, labels,
                                    [True, False],
                                    feature_fns,
                                    [2,5,10])
    # Print information about these results.
    
    best_result = results[0]
    worst_result = results[-1]
    print('best cross-validation result:\n%s' % str(best_result))
    print('worst cross-validation result:\n%s' % str(worst_result))
    plot_sorted_accuracies(results)
    
    print('\nMean Accuracies per Setting:')
    print('\n'.join(['%s: %.5f' % (s,v) for v,s in mean_accuracy_per_setting(results)]))
    
    # Fit best classifier.
    clf, vocab = fit_best_classifier(docs, labels, results[0])

    # Print top coefficients per class.
    print('\nTOP COEFFICIENTS PER CLASS:')
    print('negative words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 0, 5, vocab)]))
    print('\npositive words:')
    print('\n'.join(['%s: %.5f' % (t,v) for t,v in top_coefs(clf, 1, 5, vocab)]))

    # Parse test data
    test_docs, test_labels, X_test = parse_test_data(best_result, vocab)

    # Evaluate on test set.
    predictions = clf.predict(X_test)
    print('testing accuracy=%f' %
          accuracy_score(test_labels, predictions))

    print('\nTOP MISCLASSIFIED TEST DOCUMENTS:')
    print_top_misclassified(test_docs, test_labels, X_test, clf, 5)
    

if __name__ == '__main__':
    main()