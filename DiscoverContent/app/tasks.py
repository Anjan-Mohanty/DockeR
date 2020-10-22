from app.celery import celery_app as celery_app
from Objects import connections,user_objects,tweet_objects
import pandas as pd
from sklearn.cluster import DBSCAN
import datetime

@celery_app.task(bind=True,default_retry_delay=10)
def discover(self,discover_query):
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    cluster_number=discover_query['cluster_number']
    
    vector_template=[]
    tweet_vectors=[]
        
    users_t1=user_objects.user_set()
    query={'cluster_number':cluster_number}
    users_t1.get_users(query)
    users_screen_name_t1=[i.user['screen_name'] for i in users_t1.users]
        
    users_t2=user_objects.user_set()
    query={'cluster_number':{'$ne':cluster_number}}
    users_t2.get_users(query)
    users_screen_name_t2=[i.user['screen_name'] for i in users_t2.users]
    
    #setting Dates
    today=datetime.date.today()
    seven_days_back=today - datetime.timedelta(days=7)

    tweets_t1=tweet_objects.tweet_set()
        
    start=0
    for user in users_t1.users:
            
        if seven_days_back.year==today.year :
            
            query={'$and':[{'user.id':user.user['id']},
                           {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]},
                           {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
            
            tweets_t1.get_tweets(query)

        else:
            
            query={'$and':[{'user.id':user.user['id']},
                           {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]}]}
            
            tweets_t1.get_tweets(query)
            
            query={'$and':[{'user.id':user.user['id']},
                           {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
            
            
            tweets_t1.get_tweets(query)
            
        end=len(tweets_t1.tweets)
            
        tweets_t1.preprocess_tweets_range(start,end)
            
        ut1={}
        ut2={}
        ut3={}
            
        vector_template.append(user.user['screen_name'])
            
        for tweet in tweets_t1.tweets[start:end]:
                
            t1=0
            t2=0
            t3=0
                
            for member in tweet.tweet_mentions:
                    
                vector_template.append(member)
                    
                if member in users_screen_name_t1:
                        
                    t1+=1
                    if member not in ut1:
                        ut1[member]=1
                    else:
                        ut1[member]+=1
                    
                elif member in users_screen_name_t2:
                        
                    t2+=1
                    if member not in ut2:
                        ut2[member]=1
                    else:
                        ut2[member]+=1
                    
                else:
                        
                    t3+=1
                    if member not in ut3:
                        ut3[member]=1
                    else:
                        ut3[member]+=1
                
            t1+=1
                
            maxt=max(t1,t2,t3)
                
            if maxt==t1:
                tier=1
            elif maxt==t2:
                tier=2
            else:
                tier=3
                
            tweet.tweet['tier']=tier
        
        if len(ut1)==0:
            t1_screen_name=''
            t1_interactions=0
        else:
            t1_screen_name=max(ut1)
            t1_interactions=ut1[max(ut1)]
        
        if len(ut2)==0:
            t2_screen_name=''
            t2_interactions=0
        else:
            t2_screen_name=max(ut2)
            t2_interactions=ut2[max(ut2)]
        
        if len(ut3)==0:
            t3_screen_name=''
            t3_interactions=0
        else:
            t3_screen_name=max(ut3)
            t3_interactions=ut3[max(ut3)]
        
        
        tier1={'screen_name':t1_screen_name,'interactions':t1_interactions}
        tier2={'screen_name':t2_screen_name,'interactions':t2_interactions}
        tier3={'screen_name':t3_screen_name,'interactions':t3_interactions}
            
        query={'user.screen_name':user.user['screen_name']}
        payload={'$set':{'bond_stats':{'tier1':tier1,'tier2':tier2,'tier3':tier3}}}
        mongo_app.db.community.update(query,payload)
        start=end
        
    vector_template=list(set(vector_template))
        
    for tweet in tweets_t1.tweets:
            
        vector=[]
        for member in vector_template:
                
            if((member in tweet.tweet_mentions) or (member==tweet.tweet_user_screen_name)):
                time=1+float(tweet.tweet['created_day']/4)+float(0.25*tweet.tweet['tweeted_hour']/24)
            else:
                time=0
                
            vector.append(time)
            
        day=float(tweet.tweet['created_day']/4)
        hour=float(0.25*tweet.tweet['tweeted_hour']/24)
            
        vector.append(day)
        vector.append(hour)
            
        tweet_vectors.append(vector)
    
    if len(tweet_vectors)==0:
        return(f'No tweets - {cluster_number}')
    
    #clustering
    df=pd.DataFrame(tweet_vectors)
    clustring=DBSCAN(eps=0.25,min_samples=1).fit(df)
        
    for i in range(len(clustring.labels_)):
            
        tweets_t1.tweets[i].tweet['thread_number']=clustring.labels_[i]
        
        
        
    tweet_df=pd.DataFrame([tweet.tweet for tweet in tweets_t1.tweets])
        
    columns_to_remove=['_id','id_str','truncated', 'entities',
                       'source', 'in_reply_to_status_id', 'in_reply_to_status_id_str',
                       'in_reply_to_user_id', 'in_reply_to_user_id_str',
                       'in_reply_to_screen_name', 'geo', 'coordinates', 'place',
                       'contributors', 'is_quote_status',
                       'favorited', 'retweeted', 'lang',
                       'downloaded_day_year', 'downloaded_year',
                       'extended_entities', 'possibly_sensitive', 'quoted_status_id',
                       'quoted_status_id_str', 'quoted_status', 'retweeted_status']

    for column in columns_to_remove:
        try:
            tweet_df.drop(column,axis=1,inplace=True)
        except Exception as e:
            pass
        
    tweet_df['screen_name']=tweet_df['user'].apply(lambda x:x['screen_name'])
    tweet_df['friends_count']=tweet_df['user'].apply(lambda x:x['friends_count'])
    tweet_df['followers_count']=tweet_df['user'].apply(lambda x:x['followers_count'])
    tweet_df.drop('user',axis=1,inplace=True)

    tweet_df['tweeted_at']=tweet_df.apply(lambda row:datetime.datetime(row.created_year,1,1,row.tweeted_hour)+datetime.timedelta(row.created_day-1),axis=1)

    tweet_df['tweet_url']=tweet_df.apply(lambda row:f'https://twitter.com/{row.screen_name}/status/{row.id}',axis=1)
    
        
    tier=1
    while(tier<=3):
            
        temp_df=tweet_df[tweet_df['tier']==tier]
        
        if len(temp_df)==0:
            print(f'{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number},{tier}-{cluster_number}')
        else:
            print(f'{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*,{tier}-{cluster_number}*')
        thread_df={}

        thread_df['thread_number']=list(temp_df.groupby('thread_number').count().reset_index()['thread_number'])

        time_stamps=[]
        count=[]
        for i in thread_df['thread_number']:
    
            time_df=temp_df[temp_df['thread_number']==i]
            time_stamps.append(min(time_df['tweeted_at']))
            count.append(len(time_df))

        thread_df['time_stamps']=time_stamps
        thread_df['count']=count

        thread_df=pd.DataFrame(thread_df)
            
        plot_df=pd.DataFrame(thread_df.groupby('time_stamps').count().reset_index()['time_stamps'])
        plot_df['thread_count']=thread_df.groupby('time_stamps').count().reset_index()['count']
        plot_df['tweet_count']=thread_df.groupby('time_stamps').sum().reset_index()['count']
        
        stamps=list(plot_df[plot_df['thread_count']>(plot_df['thread_count'].mean()+2*plot_df['thread_count'].std())]['time_stamps'])
            
        for i in thread_df['thread_number']:
                
            time_df=temp_df[temp_df['thread_number']==i]
                
            time_stamp=min(time_df['tweeted_at'])
                
            if time_stamp in stamps:
                    
                for j in range(len(time_df)):
                        
                    id=int(time_df.iloc[j]['id'])
                    temp_tier=int(time_df.iloc[j]['tier'])
                    thread_number=i
                    discover=True
                       
                    query={'id':id}
                    payload={'$set':{'tier':temp_tier,'thread_number':thread_number,'discover':discover,'cluster_number':cluster_number}}
                        
                    mongo_app.db.tweets.update(query,payload)
                        
            else:
                    
                for j in range(len(time_df)):
                        
                    id=int(time_df.iloc[j]['id'])
                    temp_tier=int(time_df.iloc[j]['tier'])
                    thread_number=i
                    discover=False
                        
                    query={'id':id}
                    payload={'$set':{'tier':temp_tier,'thread_number':thread_number,'discover':discover,'cluster_number':cluster_number}}
                        
                    mongo_app.db.tweets.update(query,payload)
        
        tier+=1
            
            
