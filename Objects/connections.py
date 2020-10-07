import tweepy
import pymongo

class mongo(object):
    
    def __init__(self):
        
        self.client=None
        self.db=None
    
    def connect_to_mongo(self):
        
        self.client=pymongo.MongoClient(host='mongodb',port=27017,username='mongo',password='password',maxPoolSize=200,connect=False)

        self.db=self.client.twitter
        
def get_auth(number):
    
    mongo_app=mongo()
    mongo_app.connect_to_mongo()
    
    auth=[]
    for each in mongo_app.db.auth.find({}):
        auth.append(each)
    
    return(auth[number])

def connect_to_twitter(auth):
    
    auth_details=tweepy.OAuthHandler(auth['api_key'],auth['api_secrete_key'])
    auth_details.set_access_token(auth['access_token'],auth['access_token_secret'])

    api=tweepy.API(auth_details,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    
    return api

class twitter_api_key(object):
    
    def __init__(self):
        
        self.api_key=None
        self.api_secrete_key=None
        self.access_token=None
        self.access_token_secret=None
        
    def make_key(self,api_key,api_secrete_key,access_token,access_token_secret):
        
        self.api_key=api_key
        self.api_secrete_key=api_secrete_key
        self.access_token=access_token
        self.access_token_secret=access_token_secret
      
    def make_json(self):
        
        key={}
        key['api_key']=self.api_key
        key['api_secrete_key']=self.api_secrete_key
        key['access_token']=self.access_token
        key['access_token_secret']=self.access_token_secret
        
        return key
    
    def connect_to_twitter(self):
    
        auth_details=tweepy.OAuthHandler(self.api_key,self.api_secrete_key)
        auth_details.set_access_token(self.access_token,self.access_token_secret)

        api=tweepy.API(auth_details,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    
        return api

class twitter_api_keys(object):
    
    def __init__(self):
        
        self.keys=[]
        self.key_ids=[]
        
    def get_existing_keys(self,no_of_keys=None):
        
        mongo_app=mongo()
        mongo_app.connect_to_mongo()
        
        for key in mongo_app.db.auth.find({}):
            
            self.key_ids.append(key['_id'])
            
            key_object=twitter_api_key()
            key_object.make_key(key['api_key'],key['api_secrete_key'],key['access_token'],key['access_token_secret'])
            
            self.keys.append(key_object)
            
        if no_of_keys is not None:
            
            self.keys=self.keys[:no_of_keys]
            self.key_ids=self.key_ids[:no_of_keys]
        