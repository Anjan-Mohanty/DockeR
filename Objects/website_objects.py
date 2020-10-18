import streamlit as st
import datetime
import requests
from Objects import connections
import pandas as pd
import time

#masterobject
###############################################################################
class website(object):
    pass
###############################################################################





#main objects
###############################################################################


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
            
            st.write(f"Scheduled hour is {self.query['scheduled_hour']}")
            st.write(f"Live count of number of tweets downloaded : {count}")
            st.write(f"The User whose friends are being collected {self.query['friends_user']['screen_name']}")
            st.write(f"Today's day of year is {int(datetime.datetime.today().strftime('%j'))}")
            
            x=[self.query['duration'],self.query['last_day'],self.query['quantity'],self.query['tweets_status'],self.query['tweets_user'],self.query['user_friends_status'],self.query['year']]
            
            df=pd.DataFrame(x,index=['Tweets Collected Time Frame','Tweets Collected Last Day','Tweets Collected','Tweets Collection Status','Tweets Collected Latest User','Friends Collection Status','Year'])
            
            st.dataframe(df)

        except Exception as e:
            pass





















class user_manager(object):
    pass

class get_insights(object):
    pass
###############################################################################





#daughters of main objects
###############################################################################

#auth_keys object--------------------------------------------------------------
class auth_keys(object):
    
    def __init__(self):
        
        self.key=connections.twitter_api_key()
        
    def get_keys(self):
        
        self.key.api_key=str(st.text_input('Please Enter API key'))
        self.key.api_secrete_key=str(st.text_input('Please Enter API secret key'))
        self.key.access_token=str(st.text_input('Please Enter Access token'))
        self.key.access_token_secret=str(st.text_input('Please Enter Access token secret'))        

    def is_correct(self):
        
        if(self.key.api_key==None or self.key.api_key=='' or self.key.api_secrete_key==None or self.key.api_secrete_key=='' or self.key.access_token==None or self.key.access_token=='' or self.key.access_token_secret==None or self.key.access_token_secret==''):
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
                st.write('Please enter details properly')
                st.stop()
            else:
                
                key_json=self.key.make_json()
                
                mongo_app=connections.mongo()
                mongo_app.connect_to_mongo()
                
                mongo_app.db.auth.insert(key_json)
                st.write('**To Delete key, Use Mongo Compass.**')
                msg='The Twitter API Key is Added, Now you can collect more Data efficiently'
                st.success(msg)
                

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
        
        #query={'created_day':int(datetime.datetime.now().strftime('%j')),
        #       'created_year':int(datetime.datetime.now().year),
        #       'made_user':False}
        
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
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        if st.button('Show preview'):
            member=[]
            for i in mongo_app.db.users.find({}):
                member.append(i)
            df=pd.DataFrame(member,columns=['screen_name','core_user','status','activity','created_year','created_day','made_user'])
            st.dataframe(df)
    
    def finilize(self):
        
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
                    st.success('Muted Users')
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
            