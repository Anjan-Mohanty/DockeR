import streamlit as st
import pymongo
import datetime



#connecting to db
client=pymongo.MongoClient(host='mongodb',port=27017,username='mongo',password='password')
#client=pymongo.MongoClient('mongodb://mongodb:27017/')
db=client.twitter



#masterobject
###############################################################################
class website(object):
    pass
###############################################################################





#main objects
###############################################################################
class data_collection(website):
    pass

class user_manager(website):
    pass

class get_insights(website):
    pass
###############################################################################





#daughters of main objects
###############################################################################

#auth_keys object--------------------------------------------------------------
class auth_keys(data_collection):
    
    def __init__(self):
        
        self.existing_keys=[]
        
        self.api_key=None
        self.api_secrete_key=None
        self.access_token=None
        self.access_token_secret=None
    
    def make_json(self):
        
        key={}
        key['api_key']=self.api_key
        key['api_secrete_key']=self.api_secrete_key
        key['access_token']=self.access_token
        key['access_token_secret']=self.access_token_secret
        
        return key
    
    def push_to_auth_collection(self,key):
        try:
            db.auth.insert(key)
        except Exception as e:
            print(e)
    
    def is_correct(self):
        
        if(self.api_key==None or self.api_key=='' or self.api_secrete_key==None or self.api_secrete_key=='' or self.access_token==None or self.access_token=='' or self.access_token_secret==None or self.access_token_secret==''):
            return False
        else:
            return True
    
    def is_repeated(self):
        
        count=0
        
        for key in self.existing_keys:
            
            if(self.api_key==key.api_key or self.api_secrete_key==key.api_secrete_key or self.access_token==key.access_token or self.access_token_secret==key.access_token_secret):
                count=1
                break
        
        if count==0:
            return False
        else:
            return True
        
        
    def get_keys(self):
        
        #label='Please Enter {key} :'
        self.api_key=str(st.text_input('Please Enter API key'))
        self.api_secrete_key=str(st.text_input('Please Enter API secret key'))
        self.access_token=str(st.text_input('Please Enter Access token'))
        self.access_token_secret=str(st.text_input('Please Enter Access token secret'))
    
    def get_existing_keys(self):
        
        try:
            for key in db.auth({}):
                self.existing_keys.append(key)
        except Exception as e:
            print(e)
    
    def is_auth_added(self):
        
        if(st.button('Add API Keys')):
            
            correct=self.is_correct()
            repeated=self.is_repeated()
            
            if(repeated or not correct):
                st.write('Please enter details properly')
                st.stop()
            else:
                
                key=self.make_json()
                self.push_to_auth_collection(key)
                st.write('**To Delete key, Use Mongo Compass.**')
                msg='The Twitter API Key is Added, Now you can collect more Data efficiently'
                st.success(msg)
                

#add_user object---------------------------------------------------------------
class add_user(user_manager):
    
    def __init__(self):
        
        self.screen_name=None
        self.core_user=None
        self.status=None
        self.activity=7
        self.created_day=None
        self.created_year=None
        
    def assign_date(self):
        
        today=datetime.date.today()
        self.created_day=int(today.strftime('%j'))
        self.created_year=int(today.year)
    
    def get_screen_name(self):
        
        label='Enter the Screen name of the user @'
        self.screen_name=str(st.text_input(label))
    
    def is_core_user(self):
        
        label=f'Is @{self.screen_name} a Core User ?'
        options=[None,'Yes','No']
        self.core_user=st.radio(label,options)
    
    def get_user_status(self):
        
        label='Please select one option regarding the user'
        options=[None,'Discover','Mute','Block']
        self.status=st.radio(label,options)
        
    def make_json(self):
        
        user={}
        user['screen_name']=self.screen_name
        user['core_user']=self.core_user
        user['status']=self.status
        user['activity']=self.activity
        user['created_year']=self.created_year
        user['created_day']=self.created_day
        
        return user
    
    def push_to_users_collection(self,user):
        
        #try:
        #    db.users.remove({})
        #except Exception as e:
        #   print(e)
        
        db.users.insert(user)

    def is_user_added(self):
        
        if(st.button('Done')):
            
            if(self.screen_name==None or self.core_user==None or self.status==None or self.screen_name==''):
                st.write('Please enter details properly')
                st.stop()
            else:
                
                user=self.make_json()
                self.push_to_users_collection(user)
                msg=f'@{self.screen_name} is added, Is Core user : {self.core_user}, @{self.screen_name} will be {self.status}, date is {self.created_day}'
                st.success(msg)

