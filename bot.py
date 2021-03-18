#!/usr/bin/env python3

import database as db
import browser
import twitter

def main():
    #database = "twitter_db.sqlite"
    #conn = db.create_connection(database)

    # ID = 96879107
    twitter_handles = 'Pokemon'
    tweeter = twitter.Tweeter()
    
    user = tweeter.user_lookup(twitter_handles)
    print(user)
    tweets = tweeter.get_tweets_by_handle('Pokemon',10)
    for tweet in tweets:
        tweet.print()
    #print(lookup_resp)

    #usertweets_resp = get_tweets("96879107")



if __name__ == "__main__":
    main()


