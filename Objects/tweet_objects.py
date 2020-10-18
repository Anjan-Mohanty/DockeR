from Objects import connections











class Tweet(object):
    
    def __init__(self,tweet_json):
        
        self.tweet=tweet_json
        self.tweet_type=None
        self.tweet_user_screen_name=None
        self.tweet_mentions=None
    
    def preprocess(self):
        
        directed=[]
        
        #default type
        tweet_type='tweet'
        
        #retweet
        if 'retweeted_status' in self.tweet:
            
            tweet_type='retweet'
            
            for member in self.tweet['entities']['user_mentions']:
                directed.append(member['screen_name'])
        
        #quote
        if 'quoted_status' in self.tweet:
            
            tweet_type='quote'
            
            for member in self.tweet['entities']['user_mentions']:
                directed.append(member['screen_name'])
            
            for member in self.tweet['quoted_status']['entities']['user_mentions']:
                directed.append(member['screen_name'])
            
            directed.append(self.tweet['quoted_status']['user']['screen_name'])
        
        #reply
        if self.tweet['in_reply_to_status_id']:
            
            tweet_type='reply'
            
            for member in self.tweet['entities']['user_mentions']:
                directed.append(member['screen_name'])
        
        #if only tweet but has mentions
        for member in self.tweet['entities']['user_mentions']:
                directed.append(member['screen_name'])
        
        #now removing repeated
        directed=list(set(directed))
        
        try:
            directed.remove(self.tweet['user']['screen_name'])
        except:
            pass
        
        self.tweet_type=tweet_type
        self.tweet_user_screen_name=self.tweet['user']['screen_name']
        self.tweet_mentions=directed




class tweet_set(object):
    
    def __init__(self):
        
        self.tweets=[]
        
    def get_tweets(self,query):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        for each_tweet in mongo_app.db.tweets.find(query):
            
            tweet=Tweet(each_tweet)
            self.tweets.append(tweet)
    
    def preprocess_tweets(self):
        
        for each_tweet in self.tweets:
            
            each_tweet.preprocess()