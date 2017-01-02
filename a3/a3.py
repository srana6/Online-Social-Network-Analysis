# coding: utf-8

# # Assignment 3:  Recommendation systems
#
# Here we'll implement a content-based recommendation algorithm.
# It will use the list of genres for a movie as the content.
# The data come from the MovieLens project: http://grouplens.org/datasets/movielens/

# Please only use these imports.
from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import urllib.request
import zipfile

def download_data():
    """ DONE. Download and unzip data.
    """
    url = 'https://www.dropbox.com/s/h9ubx22ftdkyvd5/ml-latest-small.zip?dl=1'
    urllib.request.urlretrieve(url, 'ml-latest-small.zip')
    zfile = zipfile.ZipFile('ml-latest-small.zip')
    zfile.extractall()
    zfile.close()


def tokenize_string(my_string):
    """ DONE. You should use this in your tokenize function.
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    Append a new column to the movies DataFrame with header 'tokens'.
    This will contain a list of strings, one per token, extracted
    from the 'genre' field of each movie. Use the tokenize_string method above.

    Note: you may modify the movies parameter directly; no need to make
    a new copy.
    Params:
      movies...The movies DataFrame
    Returns:
      The movies DataFrame, augmented to include a new column called 'tokens'.

    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    ###TODO
    movies['tokens'] = ""
    
    for i,row in movies.iterrows():
        movies.set_value(i,'tokens',tokenize_string(row['genres']))
       
    return (movies)
    pass


def featurize(movies):
    """
    Append a new column to the movies DataFrame with header 'features'.
    Each row will contain a csr_matrix of shape (1, num_features). Each
    entry in this matrix will contain the tf-idf value of the term, as
    defined in class:
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document (movie)
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents (movies)
    df(i) is the number of unique documents containing term i

    Params:
      movies...The movies DataFrame
    Returns:
      A tuple containing:
      - The movies DataFrame, which has been modified to include a column named 'features'.
      - The vocab, a dict from term to int. Make sure the vocab is sorted alphabetically as in a2 (e.g., {'aardvark': 0, 'boy': 1, ...})
    """
    ###TODO
    genreSet=set()
    movies['features'] = "" 
    rowVal=" "
    ### MAKE A SET OF ALL UNIQUE GENRES ####
    
    for i,row in movies.iterrows():
        rowVal=row['tokens']
        genreSet.update(rowVal)
        
    sortedGenreSet=sorted(genreSet)
    
    ### VOCAB AND DF(I) ####
    vocab={}
    dfDict={}
    count=0
    for eachTerm in sortedGenreSet:
        vocab[eachTerm]=count
        count+=1
        counter=0
        for i,row in movies.iterrows():
            uniqueSet=set()
            genreTokens=row['tokens']
            uniqueSet.update(genreTokens)
            
            if eachTerm in uniqueSet:
                counter+=1
            elif eachTerm not in uniqueSet:
                continue
        dfDict[eachTerm]=counter
    
    #### CALCULATION OF tf(i, d) & max_k tf(k, d) ####
    tfIdDict={}
    max_ktfDict={}
    
    k=0
    while k<len(sortedGenreSet):
        movieGenre=sortedGenreSet[k]
        dummyList=[]
        for i,rows in movies.iterrows():
            movieGenreToken=rows['tokens']
            listOfMostCommonTokens=Counter(movieGenreToken).most_common()
            maxFreqTermPerDoc=listOfMostCommonTokens[0]
            max_ktfDict[i]=maxFreqTermPerDoc[1]
            if movieGenre in movieGenreToken:
                counting=movieGenreToken.count(movieGenre)
                tupl=(i,counting)
                dummyList.append(tupl)
            elif movieGenre not in movieGenreToken:
                counting=0
                tupl=(i,counting)
                dummyList.append(tupl)
        tfIdDict[movieGenre] = dummyList
        k+=1
                    
    
    #### CALCULATION OF tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i)) ####
    
    def calculatetfidf(vals,max_ktfDict,dfDict):
        tfidfVal=float( vals / max_ktfDict)*float( math.log10( len(movies) / dfDict ) )
        
        return tfidfVal
    
    for i,row in movies.iterrows():
        rowValuesForCsr=[]
        columnValuesForCsr=[]
        data=[]
        genreList=row['tokens']
        for genr in genreList:
            for tupList in tfIdDict[genr]:
                if tupList[0] == i:
                    vals = tupList[1]
                    break
                else:
                    continue
            tfidfVal= calculatetfidf(vals,max_ktfDict[i],dfDict[genr])
            data.append(tfidfVal)
            rowValuesForCsr.append(0)
            columnValuesForCsr.append(vocab[genr])
        
        movies.set_value(i, 'features', csr_matrix((data, (rowValuesForCsr,columnValuesForCsr)), shape=(1,len(sortedGenreSet))))
  
    return(movies,vocab)
 
    pass


def train_test_split(ratings):
    """DONE.
    Returns a random split of the ratings matrix into a training and testing set.
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]


def cosine_sim(a, b):
    """
    Compute the cosine similarity between two 1-d csr_matrices.
    Each matrix represents the tf-idf feature vector of a movie.
    Params:
      a...A csr_matrix with shape (1, number_features)
      b...A csr_matrix with shape (1, number_features)
    Returns:
      The cosine similarity, defined as: dot(a, b) / ||a|| * ||b||
      where ||a|| indicates the Euclidean norm (aka L2 norm) of vector a.
    """
    ###TODO
    
    cosineSimResult = np.divide(np.dot(a.toarray(), b.toarray().reshape(22,1)), np.multiply(np.linalg.norm(a.toarray()), np.linalg.norm(b.toarray())))
    
    return (cosineSimResult.item())

    pass


def make_predictions(movies, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, predict the ratings for each
    row in ratings_test.

    To predict the rating of user u for movie i: Compute the weighted average
    rating for every other movie that u has rated.  Restrict this weighted
    average to movies that have a positive cosine similarity with movie
    i. The weight for movie m corresponds to the cosine similarity between m
    and i.

    If there are no other movies with positive cosine similarity to use in the
    prediction, use the mean rating of the target user in ratings_train as the
    prediction.

    Params:
      movies..........The movies DataFrame.
      ratings_train...The subset of ratings used for making predictions. These are the "historical" data.
      ratings_test....The subset of ratings that need to predicted. These are the "future" data.
    Returns:
      A numpy array containing one predicted rating for each element of ratings_test.
    """
    ###
    result=[]
    movieIndex=movies.set_index(['movieId'])
    for index, row in ratings_test.iterrows():
        featureCsrMatrixTest=movieIndex.loc[row['movieId']]['features']
        n=0
        ratingsum=0
        finalCosineRatingMul=0
        finalCosineResult=0
        for index1, row1 in ratings_train[ratings_train.userId == row['userId']].iterrows():
            if row1['userId']==row['userId']:
                n +=1;
                featureCsrMatrixTrain=movieIndex.loc[row1['movieId']]['features']
                cosineResult=cosine_sim(featureCsrMatrixTest,featureCsrMatrixTrain)
                rating=row1['rating']
                ratingsum +=rating
                if  cosineResult > 0:
                        finalCosineRatingMul += cosineResult*rating
                        finalCosineResult += cosineResult
                else:
                    continue
        if finalCosineRatingMul==0:
            result.append(ratingsum/n)
        else:
            result.append(finalCosineRatingMul/finalCosineResult)
    return np.array(result)
    
    pass


def mean_absolute_error(predictions, ratings_test):
    """DONE.
    Return the mean absolute error of the predictions.
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()


def main():
    download_data()
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test)
    print('error=%f' % mean_absolute_error(predictions, ratings_test))
    print(predictions[:10])


if __name__ == '__main__':
    main()
