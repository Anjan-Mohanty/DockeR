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

class User(object):
    
    def __init__(self):
        
        self.user={}
        self.core_user=None
        self.activity=0
        self.day_added=None
        self.year_added=None
        self.cluster_number=0
        self.friends_id=[]
        self.edges=[]
    
    def make_new_user(self,user_json,api):
        
        new_user=api.get_user(id=user_json['screen_name'])
        new_user_json=new_user._json
        
        self.user['screen_name']=new_user_json['screen_name']
        self.user['id']=new_user_json['id']
        self.user['id_str']=new_user_json['id_str']
        self.user['name']=new_user_json['name']
        
        if user_json['core_user']=='Yes':
            self.core_user=True
        else:
            self.core_user=False
        
        self.day_added=user_json['created_day']
        self.year_added=user_json['created_year']
        
        mongo_app=mongo()
        mongo_app.connect_to_mongo()
        
        mongo_app.db.users.update({'_id':user_json['_id']},{'$set':{'made_user':True}})
        
    def make_user_json(self):
        
        user_dict={}
        
        user_dict['user']={}
        user_dict['user']['screen_name']=self.user['screen_name']
        user_dict['user']['id']=self.user['id']
        user_dict['user']['id_str']=self.user['id_str']
        user_dict['user']['name']=self.user['name']
        user_dict['friends_id']=self.friends_id
        user_dict['edges']=self.edges
        
        user_dict['core_user']=self.core_user
        user_dict['activity']=self.activity
        user_dict['day_added']=self.day_added
        user_dict['year_added']=self.year_added
        user_dict['cluster_number']=self.cluster_number
        
        return user_dict

class user_set(object):
    
    def __init__(self):
        
        self.users=[]
    
    def make_new_users(self,query):
        
        mongo_app=mongo()
        mongo_app.connect_to_mongo()
        
        users=[]
        for member in mongo_app.db.users.find({'$and':[{'status':query['status']},{'created_year':query['created_year']},{'created_day':query['created_day']},{'made_user':query['made_user']}]}):
            users.append(member)
        
        auth=get_auth(0)
        api=connect_to_twitter(auth)
        
        for member in users:
            
            new_user=User()
            new_user.make_new_user(member,api)
            
            self.users.append(new_user)
    
    def push_to_community(self):

        mongo_app=mongo()
        mongo_app.connect_to_mongo()        
        
        
        for user in self.users:
            
            user_json=user.make_user_json()
            
            mongo_app.db.community.insert(user_json)
        
        



        
        
        
        