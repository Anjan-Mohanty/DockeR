import streamlit as st
import datetime
import requests
from Objects import connections



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
                
                query={'report':'data_collection','scheduled_hour':hour,'last_day':int(lastDate.strftime('%j')),'year':lastDate.year,'tweets_status':'collected','user_friends_status':'collected','tweets_user':'','friends_user':{'screen_name':'','user_no':0,'type':'old'}}
                
                mongo_app.db.reports.insert(query)
            
            else:
                
                mongo_app.db.reports.update({'report':'data_collection'},{'$set':{'scheduled_hour':hour}})
            
            st.success(f'Changed to {hour} hour')

        try:
            reports=[]
            for report in mongo_app.db.reports.find({'report':'data_collection'}):
                reports.append(report)
            
            self.query=reports[0]
        
            st.write(f"Scheduled Hour : {self.query['scheduled_hour']}")
            st.write(f"Today (ie; Day of this year) : {datetime.datetime.today().strftime('%j')}")
            st.write(f"Last day collected : {self.query['last_day']}")
            st.write(f"Tweets Status : {self.query['tweets_status']}")
            st.write(f"Collecting tweets of user : {self.query['tweets_user']}")
            st.write(f"User Friends Status : {self.query['user_friends_status']}")
            st.write(f"Collecting friends of user : {self.query['friends_user']['screen_name']}")

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
            
            today=datetime.date.today()
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

