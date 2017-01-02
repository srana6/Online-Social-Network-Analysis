"""
Created on Thu Dec  1 09:20:50 2016

@author: Sumit Rana
"""

# coding: utf-8

"""
collect.py

"""

# Imports you'll need.
from collections import Counter
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI
import json
from pprint import pprint

consumer_key = 'Bcm4Oaf8sracOPujlWQRfhJ9c'
consumer_secret = 'pedc0RKlxAaMkSKx8fVboKN0zXweDZ3vqf5AqsHbVqlj69XLOz'
access_token = '771102994343485440-l0MWJWorkaVJJiapLFM80uQIhRMOIvZ'
access_token_secret = '11NT4uaBgCztj5HAiNCwENTmfZdDSAT3sddd22hMuhjIF'


write_response_in_file = 'Edward.json'
# This method is done for you. Make sure to put your credentials in the file twitter.cfg.
def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

def write_into_file_method(write_response_file, tweet_statuses_list):
    
    with open(write_response_file, 'a') as fileWriter:
        fileWriter.write(json.dumps(tweet_statuses_list))
        fileWriter.write("\n")
        

def fetch_min_tweet_id(list_of_tweets):
    
    """ 
    Fetching the minimum tweet id out of all the ids so that next time tweet result is
    ID less than (that is, older than) or equal to the specified ID
    """
    list_of_ids = []
    for tweet in list_of_tweets:
        tweet_id=tweet['id_str']
        list_of_ids.append(tweet_id)
    return sorted(list_of_ids)[0]
 
def robust_request(twitter,resource, params):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    #tweet_statuses_list = []
    response = twitter.request(resource, params)         
    if response.status_code == 200:
        data = response.json()
    else:
        print('Got error %s \nsleeping for 15 minutes.' % response.text)
        sys.stderr.flush()
        time.sleep(61 * 15)
        
    return data
 
def get_tweets(twitter, screen_name, count_value):
    """ Return a list of Twitter IDs for users that this person follows, up to 5000.
    See https://dev.twitter.com/rest/reference/get/friends/ids

    Note, because of rate limits, it's best to test this method for one candidate before trying
    on all candidates.
    """
    ###TODO
    count = 0
    ids = 0
    while True:
        if not ids:
            params = {'q': screen_name +'-filter:retweets', 'count': count_value, 'lang':'en'}
            
        params = {'q': screen_name +'-filter:retweets', 'count': count_value, 'lang':'en', 'max_id': ids}
        data_recieved=robust_request(twitter,'search/tweets',params)
        
        ids = int( fetch_min_tweet_id(data_recieved['statuses']) ) 	# this should get min id of all tweets
        
        count += len(data_recieved['statuses']) 	
            
        write_into_file_method(write_response_in_file, data_recieved['statuses'])   
        if count >= 5000:
            break
    print("DATA retrieved and stored in Edward.json")

    pass
   
def diffrentiate_fetched_data(filename):
    
    tweets_file = 'tweets.txt'
         
    with open(filename, 'r',encoding='utf-8') as fp:
        for line in fp:
            tweets_list = json.loads(line)
            
            file_for_tweets = open(tweets_file, 'a',encoding='utf-8')
            for tweets in tweets_list:
                user = tweets['user']
                tweet_text = ' '.join(t for t in str(tweets['text']).split())
                file_for_tweets.write(user['id_str']+ " || "+user['name']+ " || "+user['screen_name']+ " || "+ tweet_text+ "\n")
            file_for_tweets.close()


def get_followers(twitter, screen_name):
    """ fetches followers of user ids """
    over = False
    list_of_followers = []
    params = {'screen_name':screen_name, 'count': 5000}
    while not over:  
        data_recieved=robust_request(twitter,'followers/ids',params)
        list_of_followers = data_recieved['ids']
        print("Followers received: %s" %len(list_of_followers))
        over = True
        
    return list_of_followers

def collect_followers(twitter):
    count = 0
    follower_dict = {}
    fname='tweets.txt'
    user_dict = defaultdict(lambda:0) 
    
    with open(fname, 'r',encoding='utf-8') as fp:
        for line in fp:
            user_dict[line.split(' || ')[2]] += 1 
            top_user = sorted(user_dict.items(), key=lambda x:x[1], reverse=True)
	
    list_of_top_users = []
    
    for each_user_tuple in top_user:
        screen_name=each_user_tuple[0]
        list_of_top_users.append(screen_name)
   
    
    for i, screen_name in enumerate(list_of_top_users):
        followers_ids_list = get_followers(twitter, screen_name)
        if followers_ids_list:
            count += 1		
            follower_dict[screen_name] = followers_ids_list            
            if count >= 10:
                  break
    write_into_file_method('followersdata.json', follower_dict)


def main():
    """ Main method. You should not modify this. """
    twitter = get_twitter()
    print('Established Twitter connection.')
    searchTopic = 'Edward Snowden'
    countValue=100
    get_tweets(twitter,searchTopic,countValue)
    diffrentiate_fetched_data(write_response_in_file) #send Edward.json file to fetch user and tweet info
    collect_followers(twitter)

if __name__ == '__main__':
    main()

# That's it for now! This should give you an introduction to some of the data we'll study in this course.
