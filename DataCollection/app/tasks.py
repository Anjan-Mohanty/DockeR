from app.celery import celery_app
import time
import datetime
from Objects import connections
from Objects import user_objects
import tweepy

@celery_app.task(bind=True,default_retry_delay=10)
def tweets_celery_collector(self,query):
    
    #connecting to db
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    #today
    today=datetime.date.today()
    
    #connecting to twitter
    api_keys=connections.twitter_api_keys()
    api_keys.get_existing_keys(no_of_keys=1)
    
    api=api_keys.keys[0].connect_to_twitter()
    
    #setting time period
    todaydt=datetime.datetime(today.year,today.month,today.day,0,0,0)
    startDate=todaydt-datetime.timedelta(days=query['days'])
    endDate=todaydt-datetime.timedelta(days=2)
    
    #set status in db
    update_query={'$set':{f"last_day.{query['source']}":int(today.strftime('%j')),f"tweets_status.{query['source']}":'collecting',f"duration.{query['source']}":f"{startDate} - {endDate}"}}
    mongo_app.db.reports.update({'report':'data_collection'},update_query)
    

    
    #getting users
    
    users=user_objects.user_set()
    
    payload=query['user_payload']
    
    users.get_users(payload)
    
    #collect tweets
    tweets=[]
    i=0
    j=1
    count=0
    for user in users.users:
    
        i=i+1
        try:
            tmpTweets = api.user_timeline(user.user['screen_name'])
        except tweepy.TweepError:
            print('------ PRIVATE -----',i,user.user['screen_name'],j)
    
        print(i,user.user['screen_name'],j)
        for tweet in tmpTweets:
            if tweet.created_at < endDate and tweet.created_at > startDate:
                tweet._json['created_day']=int(tweet.created_at.strftime('%j'))
                tweet._json['created_year']=tweet.created_at.year
                tweet._json['tweeted_hour']=int(tweet._json['created_at'][11:13])
                tweets.append(tweet)
    
        try:
            while (tmpTweets[-1].created_at > startDate):
                print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
        
                i=i+1
        
                try:
                    tmpTweets = api.user_timeline(user.user['screen_name'], max_id = tmpTweets[-1].id)
                except tweepy.TweepError:
                    print('-----------',i,user.user['screen_name'],j)
            
                print(i,user.user['screen_name'],j)
                for tweet in tmpTweets:
                    if tweet.created_at < endDate and tweet.created_at > startDate:
                        tweet._json['created_day']=int(tweet.created_at.strftime('%j'))
                        tweet._json['created_year']=tweet.created_at.year
                        tweet._json['tweeted_hour']=int(tweet._json['created_at'][11:13])
                        tweets.append(tweet)
        except IndexError :
            print('*=*=*=*=  NO TWEETS BY  *=*=*=*=*=',user,j)
        j=j+1
        
        #updating status in reports
        mongo_app.db.reports.update({'report':'data_collection'},{'$set':{f"tweets_user.{query['source']}":user.user['screen_name']}})


    #pulling json part of tweets status collected
    tweets_json=[]
    for status in tweets:
        tweets_json.append(status._json)
        
    #removing duplicates
    ids={}
    duplicates=[]
    index=0

    for tweet in tweets_json:
    
        if tweet['id'] in ids:
            duplicates.append(index)
        else:
            ids[tweet['id']]=0
    
        index+=1
    
    for index in sorted(duplicates,reverse=True):
        del tweets[index]
    
    #inserting to database
    i=0
    for tweet in tweets_json:
    
        tweet['downloaded_day_year']=int(today.strftime('%j'))
        tweet['downloaded_year']=int(today.year)
        if '_id' in tweet:
            tweet.pop('_id')
            print(i)
        
        if not mongo_app.db.tweets.find({'id':tweet['id']}).count()>0:
            mongo_app.db.tweets.insert_one(tweet)
            count+=1
        i=i+1
    
    #set status in db
    mongo_app.db.reports.update({'report':'data_collection'},{'$set':{f"tweets_status.{query['source']}":'collected',f"quantity.{query['source']}":count}})








@celery_app.task(bind=True,default_retry_delay=10)
def user_friends_celery_collector(self,query):
    
    #connecting to db
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    #today
    today=datetime.date.today()
    
    #connecting to twitter
    api_keys=connections.twitter_api_keys()
    api_keys.get_existing_keys()
    
    #set status in db
    update_query={'$set':{f"last_day.{query['source']}":int(today.strftime('%j')),f"user_friends_status.{query['source']}":'collecting'}}
    mongo_app.db.reports.update({'report':'data_collection'},update_query)
    
    #getting users
    
    users=user_objects.user_set()
    
    payload=query['user_friends_payload']
    
    users.get_users(payload)
    
    #checking if it stopped in between
    reports=[]
    for report in mongo_app.db.reports.find({'report':'data_collection'}):
        reports.append(report)
    
    if len(reports)!=0:
        
        if reports[0]['friends_user']['type']==query['type']:
            
            if reports[0]['friends_user']['user_no']==len(users.users)-1:
                user_no=0
            elif reports[0]['friends_user']['user_no']==0:
                user_no=0
            else:
                user_no=reports[0]['friends_user']['user_no']-1
        
        else:
            user_no=0
        
        key_no=0
        api=api_keys.keys[key_no].connect_to_twitter_no_wait()
        while user_no<len(users.users):
            
            try:
                
                i=0
                friends=[]
                for id in tweepy.Cursor(api.friends_ids, screen_name=users.users[user_no].user['screen_name']).items():
                    friends.append({'id':id})
                    i=i+1
                #Printing Status
                print(i,users.users[user_no].user['screen_name'],user_no)
                #updating dB
                mongo_app.db.community.update_one({'_id':users.user_ids[user_no]}, {'$set':{'friends_id':friends}})
        
                #writing status to reports
                mongo_app.db.reports.update({'report':'data_collection'},{'$set':{'friends_user':{'screen_name':users.users[user_no].user['screen_name'],'user_no':user_no,'type':query['type']}}})
        
                user_no=user_no+1
            
            except tweepy.RateLimitError:
                
                time.sleep(60)
                
                key_no=(key_no+1)%(len(api_keys.keys))
                api=api_keys.keys[key_no].connect_to_twitter_no_wait()
                print(88)
            
            except Exception as e:
                print('skipping '+users.users[user_no].user['screen_name'])
                print(e)
                user_no+=1
                
        #set status in db
        mongo_app.db.reports.update({'report':'data_collection'},{'$set':{f"user_friends_status.{query['source']}":'collected'}})
        
            
    
