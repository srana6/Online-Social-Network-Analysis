# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 22:41:43 2016

@author: Sumit Rana
"""

#classify.py 

from urllib.request import urlopen 
from collections import Counter, defaultdict 
import time, json, sys, re, os 
from TwitterAPI import TwitterAPI 
from scipy.sparse import csr_matrix 
import urllib.request 
from io import BytesIO 
from zipfile import ZipFile 
 
 
# Logistic Regression... 
from sklearn.cross_validation import KFold 
from sklearn.linear_model import LogisticRegression 
#from sklearn.metrics import accuracy_score, confusion_matrix 
from scipy.sparse import lil_matrix 
 
 
def tokenize(string, lowercase=True, keep_punctuation=True, collapse_urls=True, collapse_mentions=True): 
    """ Split a tweet text into various tokens.""" 
    if not string: 
        return [] 
    if lowercase: 
        string = string.lower() 
    tokens = [] 
    if collapse_urls: 
        string = re.sub('http\S+', 'THIS_IS_A_URL', string) 
    if collapse_mentions: 
        string = re.sub('@\S+', 'THIS_IS_A_MENTION', string) 
    if keep_punctuation: 
        tokens = string.split() 
    else: 
        tokens = re.sub('\W+', ' ', string).split() 
    return tokens 
 
 
def read_tweets(filename): 
    """ reads all tweets, removes duplicates, & also prune them """ 
    tweets = [] 
    with open(filename, 'r', encoding='utf-8') as fp: 
        for line in fp: 
            tweets.append(line.split(" || ")[3])
    set_tweet=set(tweets)
    list_tweet=list(set_tweet)
    #tweets_list = list(set(tweets)) 
    return list_tweet 
 
 
def make_vocabulary(tokens_list): 
    vocabulary = defaultdict(lambda: len(vocabulary))  # If term not present, assign next int. 
    for tokens in tokens_list: 
        for token in tokens: 
            vocabulary[token]  # looking up a key; defaultdict takes care of assigning it a value. 
    print('%d The unique terms in vocabulary' % len(vocabulary))
    return vocabulary 
 
  
def download_afinn(): 
    afinn = dict() 
    #url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip') 
    #zipfile = ZipFile(BytesIO(url.read())) 
    #afinn_file = zipfile.open('AFINN/AFINN-111.txt') 
    with open('AFINN-111.txt', 'r',encoding='utf-8') as afinn_file: 
        for line in afinn_file:
            parts = line.strip().split() 
            if len(parts) == 2: 
                afinn[parts[0]] = int(parts[1]) 
        
    return afinn
 
 
def afinn_sentiment(terms, afinn, verbose=False): 
    
        
    pos = 0 
    neg = 0 
    for t in terms: 
        if t in afinn: 
            if afinn[t] > 0: 
                pos += afinn[t] 
            else: 
                neg += -1 * afinn[t] 
    return pos, neg 
 
 
def label_tweets(tokens_list, tweets_list, afinn): 
    
    """ Label each tweet to pos/neg """ 
    label = -1
    y_label = [] 
    for tokens in tokens_list: 
        pos, neg = afinn_sentiment(tokens, afinn) 
        if pos >= neg: 
            label = 1 
        elif neg > pos: 
            label = 0 
        y_label.append(label) 
 	
    return y_label 
 
def main():
    tokens_list =[] 
    # use Afinn to get labels for each tweet 
    afinn = download_afinn() 
 	 
    list_tweet = read_tweets('tweets.txt') 
    print("total Tweets fetched are: %s" %len(list_tweet)) 
    for text in list_tweet: 
        tokens = tokenize(text, lowercase=True, keep_punctuation=False, collapse_urls=True, collapse_mentions=True) 
        tokens_list.append(tokens) 
 
 
    vocab = make_vocabulary(tokens_list) 
    y_label = label_tweets(tokens_list, list_tweet, afinn) 
    print('The labelled tweets are:::',y_label)
 	 
 
 
if __name__ == '__main__': 
 	main() 

