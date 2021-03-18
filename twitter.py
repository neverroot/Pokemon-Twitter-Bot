# Python file that will deal with Twitter-related functions

import requests
import time
import os
import json


# Twitter class (User class()
class Tweeter():
    def __init__(self):
        self.bearer_token = auth()
        self.headers = create_headers(self.bearer_token)
        self.user_fields = ['description',
                            'created_at',
                            'entities',
                            'id',
                            'location',
                            'name',
                            'pinned_tweet_id',
                            'profile_image_url',
                            'protected',
                            'public_metrics',
                            'url',
                            'username',
                            'verified',
                            'withheld']
        self.default_user_fields = 'description,created_at,name,username,verified'
        self.tweet_fields = ['attachments',
                            'author_id',
                            'context_annotations',
                            'conversation_id',
                            'created_at',
                            'entities',
                            'geo',
                            'id',
                            'in_reply_to_user_id',
                            'lang',
                            'non_public_metrics',
                            'organic_metrics',
                            'possibly_sensitive',
                            'promoted_metrics',
                            'public_metrics',
                            'referenced_tweets',
                            'source',
                            'text',
                            'withheld']
        self.default_tweet_fields = 'id,created_at,text'

    # handles = list of twitter usernames
    def user_lookup(self,username, **kwargs):
        user_fields = self.default_user_fields
        if kwargs:
            if 'user_fields' in kwargs:
                assert ( set(kwargs.get('user_fields')).issubset(self.user_fields) == True ), "Invalid user_fields"
                user_fields = ','.join(kwargs.get('user_fields'))
            else:
                raise Exception ("Incorrect optional arugment")
        url = f"https://api.twitter.com/2/users/by?usernames={username}&user.fields={user_fields}"
        user_info = get_response(url)
        twitter_user = User(user_info)
        return twitter_user
    
    # https://api.twitter.com/2/users/2244994945/tweets?tweet.fields=created_at&max_results=100&start_time=2019-01-01T17:00:00Z&end_time=2020-12-12T01:00:00Z
    # this should return a list of Tweet objs
    def get_tweets_by_id(self,id,num, **kwargs):
        has_fields = False
        tweet_fields = self.default_tweet_fields
        if kwargs:
            if 'tweet_fields' in kwargs:
                assert( set(kwargs.get('tweet_fields')).issubset(self.tweet_fields) == True), "Invalid tweet_fields"
                tweet_fields = kwargs.get('tweet_fields')
                has_fields = True
            else:
                raise Exception ("Incorrect optional arugment")
        if num < 5:
            if has_fields:
                tweet_objs,next_token = get_tweets(id,5,tweet_fields=tweet_fields)
            else:
                tweet_objs,next_token = get_tweets(id,5)
            return tweet_objs[:num]
        tweets = []
        first = True
        next_token = None
        tweet_objs = None
        while(num >= 100):
            if num <= 104:
                if has_fields:
                    tweet_objs, next_token = get_tweets(id,num-10,next=next_token,tweet_fields=tweet_fields)
                else:
                    tweet_objs, next_token = get_tweets(id,num-10,next=next_token)
                tweets.append(tweet_objs)
                num -= 10
                if has_fields:
                    get_tweets(id,num)
                else:
                    get_tweets(id,num,tweet_fields=tweet_fields)
                tweets.append(tweet_objs)
                break
            if first:
                if has_fields:
                    tweet_objs, next_token = get_tweets(id,100,tweet_fields=tweet_fields)
                else:
                    tweet_objs, next_token = get_tweets(id,100)
                num -= 100
                tweets.append(tweet_objs)
                first = False
            else:
                if has_fields:
                    tweet_objs, next_token = get_tweets(id,100,next=next_token,tweet_fields=tweet_fields)
                else:
                    tweet_objs, next_token = get_tweets(id,100,next=next_token)
                tweets.append(tweet_objs)
                num -= 100
        if has_fields:
            tweet_objs, next_token = get_tweets(id,num,next=next_token,tweet_fields=tweet_fields)
        else:
            tweet_objs, next_token = get_tweets(id,num,next=next_token)
        tweets.append(tweet_objs)
        
            
        return [tweet for sublist in tweets for tweet in sublist]

    def get_tweets_by_handle(self,handle,num,**kwargs):
        
        # make user lookup request to get id
        user_fields = "user.fields=name,id"
        url = f"https://api.twitter.com/2/users/by?usernames={handle}&{user_fields}"
        name_id = get_response(url)

        #parse id
        id = name_id['data'][0]['id']
        
        #get tweets
        tweets = self.get_tweets_by_id(id,num,**kwargs)

        return tweets

def get_tweets(id, num, **kwargs):
    assert (num >= 5), "Number of requested tweets cannot be less than 5"
    assert (num <= 100), "Number of requested tweets cannot be more than 100"
    tweet_fields = 'id,created_at,text'
    # get json data 
    if "tweet_fields" in kwargs:
        tweet_fields = ','.join(kwargs.get('tweet_fields'))
    url = f"https://api.twitter.com/2/users/{id}/tweets?tweet.fields={tweet_fields}&max_results={num}"
    if "next" in kwargs and kwargs.get('next'):
        url = url+f"&pagination_token={kwargs.get('next')}"
    json_tweets = get_response(url)

    # parse json data and return tweet objects and next token for potential pagination
    tweet_objs = []
    for tweet in json_tweets['data']:
        tweet_objs.append(Tweet(tweet))
    next_token = json_tweets['meta']['next_token']
    return (tweet_objs,next_token)


class User():
    def __init__(self,json_dict):
        for data in json_dict['data']:
            for attr in data:
                setattr(self,attr,data[attr])
    
    def print(self):
        print("\n\n")
        print(" {:<11} | {}".format("ATTRIBUTE","VALUE"))
        print(" {:<11}   {}".format("---------","-----"))
        for attr in self.__dict__['data']:
            for key in attr:
                if isinstance(attr[key],bool) or isinstance(attr[key],int):
                    print("{:<12} | {}".format(key,attr[key]))
                else:
                    print("{:<12} | {}".format(key,attr[key].replace("\n","\n"+" "*15)))
                print("\n")    
    def raw(self):
        for attr in self.__dict__:
            print("[-]",attr)
            print("-"*len(attr))
            print(self.__dict__[attr])
            print("-"*len(attr))
        

# Tweet class
class Tweet():
    def __init__(self,json_dict):
        # set attributes of each Tweet
        # may vary depending on the tweet_fields requested in API call
        for key in json_dict:
            setattr(self, key, json_dict[key])
    def print(self):
        print("\n\n")
        print(" {:<7} | {}".format("ATTRIBUTE","VALUE"))
        print(" {:<7}   {}".format("---------","-----"))
        for attr in self.__dict__:
            print("{:<10} | {}".format(attr,self.__dict__[attr].replace("\n","\n"+" "*13)))
            print("\n")
    def raw(self):
        for attr in self.__dict__:
            print("[-]",attr)
            print("-"*len(attr))
            print(self.__dict__[attr])
            print("-"*len(attr))


# returns bearer token
def auth():
    return "AAAAAAAAAAAAAAAAAAAAAByINQEAAAAA%2FS%2F%2BbcJ5jw0Vmze9k%2Fowdo9EaL0%3DvSEn36wnfspxxsaEVi3ZPKmHAzkKubyZWWejn8oynR3ffJ32BB"
    #return os.environ.get("BEARER_TOKEN")

# returns headers
def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers

# get response w/ url
def get_response(url):
    tok = auth()
    headers = create_headers(tok)
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(parse_error(url,response.status_code,response.text))
    return response.json()

# parse error recevied from Twitter APi
def parse_error(url,code, json_dict):
    text = json.loads(json_dict)
    title  = text['title']
    detail = text['detail']
    api_url    = text['type']
    error   = f"\nURL: {url}\n" + \
            f"Error {code}: {title}\n" + \
            f"{detail}\n"
    for err in text['errors']:
        for key in err.keys():
            error += f"{key}: {err[key]}\n"
    error += f"For more help, visit: {api_url}"

    return error

        