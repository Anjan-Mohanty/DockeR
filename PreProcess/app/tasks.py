from app.celery import celery_app
from Objects import tweet_objects,user_objects,connections
import datetime

@celery_app.task(bind=True,default_retry_delay=10)
def process(self,query):
    
    weights=query['weights']
    
    user=user_objects.user_set()
    user.get_users({'user.screen_name':query['user']})
    
    user=user.users[0]
    
    all_users=user_objects.user_set()
    all_users.get_users({})
    
    user.edges=[]
    
    for each_user in all_users.users:
        
        if user.user['screen_name']!=each_user.user['screen_name']:
            
            edge={}
            edge['id']=each_user.user['id']
            edge['screen_name']=each_user.user['screen_name']
            
            is_follower=False
            for id in each_user.friends_id:
                if id['id']==user.user['id']:
                    is_follower=True
                    break
            
            edge['is_follower']=is_follower
            edge['bond']=0
            user.edges.append(edge)
    
    
    tweets=tweet_objects.tweet_set()
    
    #today and seven days back
    today=datetime.date.today()
    seven_days_back=today - datetime.timedelta(days=7)
    
    if seven_days_back.year==today.year :
        
        tweets_query={'$and':[{'user.id':user.user['id']},
                                         {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]},
                                         {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
        
        tweets.get_tweets(tweets_query)

    else:
        
        tweets_query={'$and':[{'user.id':user.user['id']},
                                         {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]}]}
        
        tweets.get_tweets(tweets_query)
        
        tweets_query={'$and':[{'user.id':user.user['id']},
                                         {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
        
        tweets.get_tweets(tweets_query)
        
    tweets.preprocess_tweets()
    
    user.activity=len(tweets.tweets)
    
    now_weights={}
    now_weights['base']=weights['tweet_weight']
    now_weights['tweet']=weights['tweet_mention_weight']
    now_weights['retweet']=weights['retweet_weight']
    now_weights['quote']=weights['quote_weight']
    now_weights['reply']=weights['reply_weight']
    
    
    for tweet in tweets.tweets:
        
        for edge in user.edges:
            
            if edge['is_follower']:
                edge['bond']=edge['bond']+now_weights['base']
            if edge['screen_name'] in tweet.tweet_mentions:
                edge['bond']=edge['bond']+now_weights[tweet.tweet_type]
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    mongo_app.db.community.update({'user.screen_name':user.user['screen_name']},{'$set':{'activity':user.activity,'edges':user.edges}})
            
            
