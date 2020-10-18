from app import app
from flask import request
from Objects import tweet_objects
from Objects import connections
from collections import Counter
import datetime
from Objects import user_objects

def get_mute_users():
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    try:
        mute_users=[]
        for user in mongo_app.db.mute.find({}):
            mute_users.append(user['screen_name'])
    except:
        pass
    
    return mute_users

    
@app.route('/',methods=['POST','GET'])
def index():
    
    query=dict(request.get_json())
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    mongo_app.db.users.remove({})
    
    tweets=tweet_objects.tweet_set()
    
    #todays day year
    day=int(datetime.date.today().strftime('%j'))
    today=datetime.date.today()
    
    if day-7>=0:
        
        query={'$and':[{'created_day':{'$gt':day-7}},{'created_year':today.year}]}
        tweets.get_tweets(query)
        
    else:
        
        query={'$and':[{'created_day':{'$gt':0}},{'created_year':today.year}]}
        tweets.get_tweets(query)
    
        last_year_days=int(datetime.datetime(today.year-1,12,31).strftime('%j'))
        query={'$and':[{'created_day':{'$gt':last_year_days+day-7}},{'created_year':today.year-1}]}
        tweets.get_tweets(query)

    
    tweets.preprocess_tweets()
    
    mute_users=get_mute_users()
    
    existing_users=user_objects.user_set()
    user_query={}
    existing_users.get_users(user_query)
    
    mute_users+=[user.user['screen_name'] for user in existing_users.users]
    
    discovered_users=[]
    for tweet in tweets.tweets:
        discovered_users+=tweet.tweet_mentions
    
    discovered_users=Counter(discovered_users)
    
    for user_screen_name in mute_users:
        
        try:
            discovered_users.pop(user_screen_name)
        except:
            pass
    
    final_users=[]
    for k,v in discovered_users.items():
    
        temp={}
    
        temp['screen_name']=k
        temp['activity']=v
    
        final_users.append(temp)

    final_users=final_users[:30]
    
    
    #extra processing
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    for user in final_users:
        
        user['core_user']=None
        user['status']=None
        user['created_year']=int(datetime.datetime.now().year)
        user['created_day']=int(datetime.datetime.now().strftime('%j'))
        user['made_user']=False
        
        mongo_app.db.users.insert(user)
    
    return('done')
    

