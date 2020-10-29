import streamlit as st
import datetime
import requests
from Objects import connections,tweet_objects
import pandas as pd
import time
from Objects import user_objects
import tweepy


#data_collection object--------------------------------------------------------
class data_collection(object):
    
    def __init__(self):
        
        self.query=None
    
    def status(self):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        label='When do you want to schedule this task every day ?(Please mention in UTC timezone)'
        hour=st.slider(label=label,min_value=0,max_value=23,value=8,step=1)
        
        if st.button('Done'):
            
            reports=[]
            for report in mongo_app.db.reports.find({'report':'data_collection'}):
                reports.append(report)
            
            if len(reports)==0:
                
                today=datetime.date.today()
                todaydt=datetime.datetime(today.year,today.month,today.day,0,0,0)
                lastDate=todaydt-datetime.timedelta(days=7)
                
                query={
                    'report':'data_collection',
                    'scheduled_hour':hour,
                    'last_day':{'scheduler':int(lastDate.strftime('%j')),'add':int(lastDate.strftime('%j')),'discover':int(lastDate.strftime('%j'))},
                    'year':{'scheduler':int(lastDate.year),'add':int(lastDate.year),'discover':int(lastDate.year)},
                    'tweets_status':{'scheduler':'collected','add':'collected','discover':'collected'},
                    'user_friends_status':{'scheduler':'collected','add':'collected','discover':'collected'},
                    'tweets_user':{'scheduler':'','add':'','discover':''},
                    'friends_user':{'screen_name':'','user_no':0,'type':'old'},
                    'duration':{'scheduler':'','add':'','discover':''},
                    'quantity':{'scheduler':0,'add':0,'discover':0}
                    }
                
                mongo_app.db.reports.insert(query)
            
            else:
                
                mongo_app.db.reports.update({'report':'data_collection'},{'$set':{'scheduled_hour':hour}})
            
            st.success(f'Changed to {hour} hour')

        try:
            reports=[]
            for report in mongo_app.db.reports.find({'report':'data_collection'}):
                reports.append(report)
            
            self.query=reports[0]
            count=mongo_app.db.tweets.find({'$and':[{'downloaded_day_year':int(datetime.datetime.today().strftime('%j'))},{'downloaded_year':datetime.datetime.today().year}]}).count()
            
            st.write(f"Scheduled hour is :{self.query['scheduled_hour']}.")
            st.write(f"Live count of number of **tweets downloaded** : {count}.")
            st.write(f"The User whose friends are being collected '{self.query['friends_user']['screen_name']}'.")
            st.write(f"Today's day of year is : {int(datetime.datetime.today().strftime('%j'))}.")
            
            x=[self.query['duration'],self.query['last_day'],self.query['quantity'],self.query['tweets_status'],self.query['tweets_user'],self.query['user_friends_status'],self.query['year']]
            
            df=pd.DataFrame(x,index=['Tweets Collected Time Frame','Tweets Collected Last Day','Tweets Collected','Tweets Collection Status','Tweets Collected Latest User','Friends Collection Status','Year'])
            
            st.dataframe(df)

        except Exception as e:
            pass



#auth_keys object--------------------------------------------------------------
class auth_keys(object):
    
    def __init__(self):
        
        self.key=connections.twitter_api_key()
        
    def get_keys(self):
        
        self.key.app_name=str(st.text_input('Please Enter App name'))
        self.key.api_key=str(st.text_input('Please Enter API key'))
        self.key.api_secrete_key=str(st.text_input('Please Enter API secret key'))
        self.key.access_token=str(st.text_input('Please Enter Access token'))
        self.key.access_token_secret=str(st.text_input('Please Enter Access token secret'))        

    def is_correct(self):
        
        if(self.key.app_name==None or self.key.app_name=='' or self.key.api_key==None or self.key.api_key=='' or self.key.api_secrete_key==None or self.key.api_secrete_key=='' or self.key.access_token==None or self.key.access_token=='' or self.key.access_token_secret==None or self.key.access_token_secret==''):
            return False
        else:
            return True

    def is_repeated(self):
        
        count=0
        
        existing_keys=connections.twitter_api_keys()
        existing_keys.get_existing_keys()
        
        for key in existing_keys.keys:
            
            if(self.key.api_key==key.api_key or self.key.api_secrete_key==key.api_secrete_key or self.key.access_token==key.access_token or self.key.access_token_secret==key.access_token_secret):
                count=1
                break
        
        if count==0:
            return False
        else:
            return True

    def is_auth_added(self):
        
        if(st.button('Add API Keys')):
            
            correct=self.is_correct()
            repeated=self.is_repeated()
            
            if(repeated or not correct):
                st.write('Please enter details properly, probabably you are missing to fill something or are trying to add same key again, if nothing solves try deleting the existing api app and add new one')
                st.stop()
            else:
            
                key_json=self.key.make_json()
                
                mongo_app=connections.mongo()
                mongo_app.connect_to_mongo()
                
                
                #testing
                api=self.key.connect_to_twitter_no_wait()
                
                try:
                    user_id='Twitter'
                    
                    user=api.get_user(id=user_id)
                
                except tweepy.RateLimitError:
                    
                    st.write('Try after 15 mins as we have exceded twitter rate limit')
                    st.stop()
                    
                except Exception as e:
    
                    if e.reason[:22]=='Failed to send request':
                        st.write('No Internet 🥱')
                        st.stop()
    
                    else:
                        st.write('There may be some mistake in the keys entered 😭')
                        st.stop()
                
                mongo_app.db.auth.insert(key_json)
                st.write('**To Delete key, Use Mongo Compass.**')
                msg='The Twitter API Key is Added, Now you can collect more Data efficiently'
                st.success(msg)
    
    def delete(self):
        
        st.write('---')
        st.write('## Delete API APP keys')
        
        app_name=str(st.text_input('Enter API APP name'))
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        mongo_app.db.auth.remove({'app_name':app_name})

#add_user object---------------------------------------------------------------
class add_user(object):
    
    def __init__(self):
        
        self.screen_name=None
        self.core_user=None
        self.status=None
        self.activity=7
        self.created_day=None
        self.created_year=None
        self.made_user=False
            
    def get_details(self):
        
        today=datetime.date.today()
        self.created_day=int(today.strftime('%j'))
        self.created_year=int(today.year)
        
        label='Enter the Screen name of the user @'
        self.screen_name=str(st.text_input(label))

        label=f'Is @{self.screen_name} a Core User ?'
        options=[None,'Yes','No']
        self.core_user=st.radio(label,options)

        label='Please select one option regarding the user'
        options=[None,'Add']
        self.status=st.radio(label,options)
        
    def make_json(self):
        
        user={}
        user['screen_name']=self.screen_name
        user['core_user']=self.core_user
        user['status']=self.status
        user['activity']=self.activity
        user['created_year']=self.created_year
        user['created_day']=self.created_day
        user['made_user']=self.made_user
        
        return user
    

    def is_user_added(self):
        
        if(st.button('Done')):
            
            if(self.screen_name==None or self.core_user==None or self.status==None or self.screen_name==''):
                st.write('Please enter details properly 🎅👵')
                st.stop()
            else:
                
                try:
                    keys=connections.twitter_api_keys()
                    keys.get_existing_keys(no_of_keys=1)
        
                    api=keys.keys[0].connect_to_twitter()
                    
                    new_user=api.get_user(id=self.screen_name)
                except Exception as e:
                    
                    if e.reason[:22]=='Failed to send request':
                        st.write('No Internet 😴')
                        st.stop()
                    
                    if e.api_code==50:
                        st.write('User not found, please check the name properly 🥱')
                        st.stop()
                        
                user=self.make_json()
                
                mongo_app=connections.mongo()
                mongo_app.connect_to_mongo()
                
                mongo_app.db.users.insert(user)
                #self.push_to_users_collection(user)
                
                
                msg=f'@{self.screen_name} is added, Is Core user : {self.core_user}, @{self.screen_name} will be {self.status}, date is {self.created_day}, Add the users and press on Make users button to add users sofar'
                st.success(msg)
    
    def make_added_users(self):
        
        if(st.button('Make Added Users')):
            
            mongo_app=connections.mongo()
            mongo_app.connect_to_mongo()
            
            today=datetime.date.today()
            
            members=[]
            for i in mongo_app.db.users.find({"status":"Add","created_year":int(today.year),"created_day":int(today.strftime('%j')),"made_user":False}):
                members.append(i['screen_name'])
                
                
            
            payload={"status":"Add","created_year":int(today.year),"created_day":int(today.strftime('%j')),"made_user":False}
            url="http://usermaker:5000/"
            with st.spinner('Wait making users'):
                
                session = requests.Session()
                session.trust_env = False
                
                report= session.post(url,json=payload)
            
            
                if(report.status_code==200):
                    st.success('Made users 😉'+' '+str(report.text))
                else:
                    st.success('Please try again 😢')
                    
            #collecting their tweets
            with st.spinner('Collecting tweets...'):
                
                #collecting tweets
                session = requests.Session()
                session.trust_env = False
                
                user_query={'user.screen_name':{'$in':members}}
                
                tweets_payload={'days':7,'user_payload':user_query,'source':'add'}
                url="http://datacollection:5010/tweets"
                
                report= session.post(url,json=tweets_payload)
                
                time.sleep(5)
                
                user_friends_query={'$and':[{'day_added':int(datetime.datetime.now().strftime('%j'))},{'year_added':int(datetime.datetime.now().year)}]}
                user_payload={'type':'new','user_friends_payload':user_friends_query,'source':'add'}
                url="http://datacollection:5010/user_friends"
                
                report= session.post(url,json=user_payload)
                    
    def delete_user(self):
        
        st.write('---')
        st.write('## Delete User')
        st.write('To delete a user, Please enter the details below')
        
        label='Enter screen_name of user'
        screen_name=str(st.text_input(label))
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        if st.button('Delete'):
            
            
            if mongo_app.db.community.find({'user.screen_name':screen_name}).count()==0:
            
                st.write(f'@{screen_name} is not their 😏')
                st.stop()
        
            else:
            
                mongo_app.db.community.remove({'user.screen_name':screen_name})
                mongo_app.db.tweets.remove({'user.screen_name':screen_name})
                st.write(f'@{screen_name} is deleted')

#discover_users object---------------------------------------------------------------
class discover_users(object):
    
    def __init__(self):
        self.users=[]
    
    def start_discovering(self):
        
        if st.button('Discover users'):
            
            with st.spinner('Discovering..'):
                
                payload={}
                url="http://discoverusers:5030/"
            
                session = requests.Session()
                session.trust_env = False
                
                report= session.post(url,json=payload)
                
                if(report.status_code==200):
                    st.success('Discovered new users 😎')
                else:
                    st.success('Please try again 😢')
            
    
    def get_users(self):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        query={'$and':[{'created_day':int(datetime.datetime.now().strftime('%j'))},{'created_year':int(datetime.datetime.now().year)},{'made_user':False}]}
        
        for member in mongo_app.db.users.find(query):
            self.users.append(member['screen_name'])
    
    def take_actions(self):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        label='Select Users to take action'
        done=st.multiselect(label,[i for i in self.users])
        
        try:
            
            user=done[-1]
            
            url=f'[{user}](https://twitter.com/{user})'
            
            st.write('@'+url+' is the selected user, Please fill the details below')
            
            activity=[]
            for i in mongo_app.db.users.find({'screen_name':user}):
                activity.append(i['activity'])
                
            st.write('The number of interactions with @'+url+' is : '+str(activity[0]))
            
            options=[None,'Discover','Mute','Block']
            label='What action do you wan to take on @'+user
            status=st.radio(label,options,index=0)
        
            options=[None,'Yes','No']
            label='Do you want @'+user+' to be Core user ?'
            core_user=st.radio(label,options,index=0)
            
            if st.button('Done'):
                
                if((status==None) or (core_user==None)):
                    st.write('Enter above details properly')
                    st.stop()
                else:
                    
                    with st.spinner('Working'):
                        
                        mongo_app.db.users.update({'screen_name':user},{'$set':{'status':status,'core_user':core_user}})
                    
                        member=[]
                        for i in mongo_app.db.users.find({'screen_name':user}):
                            member.append(i)
                    
                        label=member[0]['screen_name']+', '+member[0]['status']+', '+member[0]['core_user']
                        st.success(label)
                
        except IndexError:
            st.write('Start selecting users, After pressing Discover users button')
    
    def show_preview(self):
        
        st.write('---')
        st.write('## Show preview')
        st.write('See what all actions have been taken on the above people.')
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        if st.button('Show preview'):
            member=[]
            for i in mongo_app.db.users.find({}):
                member.append(i)
            df=pd.DataFrame(member,columns=['screen_name','core_user','status','activity','created_year','created_day','made_user'])
            st.dataframe(df)
    
    def finilize(self):
        
        st.write('---')
        st.write('## Finilize Users')
        st.write('Finilize the actions taken above.')
        if st.button('Finilize Users'):
            
            today=datetime.date.today()
            
            #getting receantly added users
            mongo_app=connections.mongo()
            mongo_app.connect_to_mongo()
            
            members=[]
            for i in mongo_app.db.users.find({"status":"Discover","created_year":int(today.year),"created_day":int(today.strftime('%j')),"made_user":False}):
                members.append(i['screen_name'])
        
            #making users
            with st.spinner('Making Users...'):
                
                
                payload={"status":"Discover","created_year":int(today.year),"created_day":int(today.strftime('%j')),"made_user":False}
                url="http://usermaker:5000/"
                
                session = requests.Session()
                session.trust_env = False
                
                report= session.post(url,json=payload)
            
            
                if(report.status_code==200):
                    st.success('Made users 😉'+' '+str(report.text))
                else:
                    st.success('Please try again 😢')
                
            
            #muting users
            with st.spinner('Muting Users...'):
                
                payload={}
                url="http://muteusers:5040/"
                
                session = requests.Session()
                session.trust_env = False
                
                report= session.post(url,json=payload)
            
            
                if(report.status_code==200):
                    st.success('Muted Users 😶')
                else:
                    st.success('Please try again 😢')
            
            #collecting their tweets
            with st.spinner('Collecting tweets...'):
                
                #collecting tweets
                session = requests.Session()
                session.trust_env = False
                
                user_query={'user.screen_name':{'$in':members}}
                
                tweets_payload={'days':7,'user_payload':user_query,'source':'discover'}
                url="http://datacollection:5010/tweets"
                
                report= session.post(url,json=tweets_payload)
                
                time.sleep(5)
                
                user_friends_query={'$and':[{'day_added':int(datetime.datetime.now().strftime('%j'))},{'year_added':int(datetime.datetime.now().year)}]}
                user_payload={'type':'new','user_friends_payload':user_friends_query,'source':'discover'}
                url="http://datacollection:5010/user_friends"
                
                report= session.post(url,json=user_payload)
            



#preprocess object-------------------------------------------------------------
class preprocess(object):
    
    def __init__(self):
        
        self.tweet_weight=None
        self.tweet_mention_weight=None
        self.retweet_weight=None
        self.quote_weight=None
        self.reply_weight=None
        
    def get_details(self):
        
        st.write('Please **adjust** the below **values** to get **best Clusters**')
        
        label='Weight for plane Tweet'
        self.tweet_weight=st.slider(label,min_value=0.000,max_value=10000.000,value=0.010,step=0.001)
        
        label='Weight for Tweet with mention'
        self.tweet_mention_weight=st.slider(label,min_value=0.000,max_value=10000.000,value=0.100,step=0.001)
        
        label='Weight for retweet'
        self.retweet_weight=st.slider(label,min_value=0.000,max_value=10000.000,value=1.000,step=0.001)
        
        label='Weight for Quote'
        self.quote_weight=st.slider(label,min_value=0.000,max_value=10000.000,value=10.000,step=0.001)
        
        label='Weight for reply'
        self.reply_weight=st.slider(label,min_value=0.000,max_value=10000.000,value=100.000,step=0.001)

        st.write('During testing the default weights were giving good results,')
        st.write('If you do not get good Clusters please adjust above weights.')
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        if st.button('Done'):
            
            reports=[]
            for i in mongo_app.db.reports.find({'report':'preprocess'}):
                reports.append(i)
            
            if len(reports)==0:
                
                mongo_app.db.reports.insert({'report':'preprocess','tweet_weight':self.tweet_weight,'tweet_mention_weight':self.tweet_mention_weight,'retweet_weight':self.retweet_weight,'quote_weight':self.quote_weight,'reply_weight':self.reply_weight})
                
            else:
                mongo_app.db.reports.update({'report':'preprocess'},{'$set':{'tweet_weight':self.tweet_weight,'tweet_mention_weight':self.tweet_mention_weight,'retweet_weight':self.retweet_weight,'quote_weight':self.quote_weight,'reply_weight':self.reply_weight}})
        
        try:
            reports=[]
            for i in mongo_app.db.reports.find({'report':'preprocess'}):
                reports.append(i)
                
            st.write('- '+f"{reports[0]['tweet_weight']}, this is the amount of bond strength gained by the followers of, if the user tweets a simple tweet.")
            st.write('- '+f"{reports[0]['tweet_mention_weight']}, this is the amount of bond strength gained by a twitter user, if a user mentions the twitter user in his tweet.")
            st.write('- '+f"{reports[0]['retweet_weight']}, this is the amount of bond strength gained by a twitter user, if a user retweets a tweet of a twitter user.")
            st.write('- '+f"{reports[0]['quote_weight']}, this is the amount of bond strength gained by a twitter user, if a user quotes a tweet of a twitter user.")
            st.write('- '+f"{reports[0]['reply_weight']}, this is the amount of bond strength gained by a twitter user, if a user replies to a tweet of a twitter user.")
        except:
            pass
        
    def process_data(self):
        
        st.write('---')
        st.write('## Start Preprocessing')
        
        st.write('**The Pre Process step below is done using parallel processing**')
        st.write('**PLEASE DO THIS STEP ONLY AFTER COLLECTING ALL THE TWEETS**')
        
        if st.button('Pre Process'):
            
            with st.spinner('Pre Processing...'):
                session = requests.Session()
                session.trust_env = False
            
                url="http://preprocess:5100/"
                payload={}
            
                report= session.post(url,json=payload)
                
                if(report.status_code==200):
                    st.success('Processed Users 😃')
                else:
                    st.success('Please try again 😢')
            
    def show_status(self):
        
        pass
    
    
class cluster_community(object):
    
    def __init__(self):
        
        self.cluster_number=None
        self.no_clusters=2
    
    def do_clustering(self):
        
        st.write('**Please do Pre Process step before this step, or else you get error results**')
        st.write('If you want to **cluster** please press the **button** below.')
        
        if st.button('Cluster Community'):
            
            with st.spinner('Clustring...'):
                
                session = requests.Session()
                session.trust_env = False
            
                url="http://clustercommunity:5300/"
                payload={}
            
                report= session.post(url,json=payload)
                
                if(report.status_code==200):
                    st.success('Clustered Community 😃')
                else:
                    st.success('Please try again 😢')
    
    
    def show_report(self):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        reports=[]
        for report in mongo_app.db.reports.find({'report':'cluster_community'}):
            reports.append(report)
        
        if len(reports)!=0:
            
            st.write(f"The present no of Users in our community are : {reports[0]['no_users']}")
            st.write(f"The number of **Clusters** detected are : {reports[0]['no_clusters']}")
            
            self.no_clusters=reports[0]['no_clusters']
            
    def show_clusters(self):
        
        label='Which Cluster would you like to see'
        self.cluster_number=st.slider(label,min_value=0,max_value=self.no_clusters-1,value=0,step=1)
        
        if st.button('Show Cluster'):
            
            users_cluster=user_objects.user_set()
            users_cluster.get_users({'cluster_number':self.cluster_number})
            
            cluster=[]
            
            for user in users_cluster.users:
                
                temp={}
                temp['User']=user.user['name']
                temp['Screen name']=user.user['screen_name']
                temp['Activity']=user.activity
                
                if user.bond_stats==None:
                    
                    temp['Tier 1']=''
                    temp['Tier 1 interactions']=0
                    
                    temp['Tier 2']=''
                    temp['Tier 2 interactions']=0
                    
                    temp['Tier 3']=''
                    temp['Tier 3 interactions']=0
                    
                else:
                    temp['Tier 1']=user.bond_stats['tier1']['screen_name']
                    temp['Tier 1 interactions']=user.bond_stats['tier1']['interactions']
                
                
                    temp['Tier 2']=user.bond_stats['tier2']['screen_name']
                    temp['Tier 2 interactions']=user.bond_stats['tier2']['interactions']
                
                    temp['Tier 3']=user.bond_stats['tier3']['screen_name']
                    temp['Tier 3 interactions']=user.bond_stats['tier3']['interactions']
                
                cluster.append(temp)
            
            
            df=pd.DataFrame(cluster)
            
            st.dataframe(df)
            
class discover_content(object):
    
    def __init__(self):
        
        self.cluster_number=None
        self.tier=None
    
    def extract_trends(self):
        
        st.write('Discover Content from the tweets, that have been tweeted this week by pressing the button below')
        st.write('Please Cluster the community before this step, Atleast once before this step')
        
        if st.button('Discover Content'):
            
            with st.spinner('Discovering Content...'):
                
                session = requests.Session()
                session.trust_env = False
            
                url="http://discovercontent:2020/"
                payload={}
            
                report= session.post(url,json=payload)
                
                if(report.status_code==200):
                    st.success('Discovered Content 😃')
                else:
                    st.success('Please try again 😢')
                    
    def get_details(self):
        
        label='Enter the Cluster number'
        self.cluster_number=st.number_input(label,value=0)
        
        label='Select tire number'
        options=[1,2,3]
        self.tier=st.radio(label,options,index=0)
    
    def show_content(self):
        
        st.write('To view Discovered Content press the button below')
        
        if st.button('Show Content'):
            
           
            with st.spinner('Preparing...'):
                
                tweets_t=tweet_objects.tweet_set()
                
                #setting Dates
                today=datetime.date.today()
                seven_days_back=today - datetime.timedelta(days=7)
                
                payload={'$and':[{'tier':self.tier},{'cluster_number':self.cluster_number},{'discover':True}]}
                
                if seven_days_back.year==today.year :
            
                    query={'$and':[payload,
                                   {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]},
                                   {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
            
                    tweets_t.get_tweets(query)

                else:
                    
                    query={'$and':[payload,
                                   {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]}]}
                    
                    tweets_t.get_tweets(query)
            
                    query={'$and':[payload,
                                   {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}
            
            
                    tweets_t.get_tweets(query)
                
                
                
                
                if len(tweets_t.tweets)==0:
                    
                    st.write('Nothing to discover or the number of tweets is very less its fine no worries 😅😉😴')
                    st.stop()
                
                def by_value(tweet):
                    
                    return(tweet.tweet['thread_number'])
                
                tweets_t.tweets.sort(key=by_value)
                
                thread_number=[tweet.tweet['thread_number'] for tweet in tweets_t.tweets]
                
                screen_name=[tweet.tweet['user']['screen_name'] for tweet in tweets_t.tweets]
                
                text=[tweet.tweet['text'] for tweet in tweets_t.tweets]
                
                def make_clickable(val):
                    # target _blank to open new window
                    return '<a target="_blank" href="{}">{}</a>'.format(val, val)
                
                tweet_url=[f"https://twitter.com/{tweet.tweet['user']['screen_name']}/status/{tweet.tweet['id']}" for tweet in tweets_t.tweets]
                
                favorite_count=[tweet.tweet['favorite_count'] for tweet in tweets_t.tweets]
                retweet_count=[tweet.tweet['retweet_count'] for tweet in tweets_t.tweets]
                created_at=[tweet.tweet['created_at'] for tweet in tweets_t.tweets]
                
                df_dict={'thread_number':thread_number,'screen_name':screen_name,'text':text,'tweet_url':tweet_url,'favorite_count':favorite_count,'retweet_count':retweet_count,'created_at':created_at}
                
                df=pd.DataFrame(df_dict)
                
                st.table(df)
                
                























