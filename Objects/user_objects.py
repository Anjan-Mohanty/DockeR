from Objects import connections




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
        
    def make_user(self,user):
        
        self.user=user['user']
        self.core_user=user['core_user']
        self.activity=user['activity']
        self.day_added=user['day_added']
        self.year_added=user['year_added']
        self.cluster_number=user['cluster_number']
        self.friends_id=user['friends_id']
        self.edges=user['edges']
        
    
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
        
        mongo_app=connections.mongo()
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
        self.user_ids=[]
    
    def make_new_users(self,query):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        mongo_app.db.users.remove({'$and':[{'created_year':{'$ne':query['created_year']}},{'created_day':{'$ne':query['created_day']}}]})
        users=[]
        for member in mongo_app.db.users.find({'$and':[{'status':query['status']},{'created_year':query['created_year']},{'created_day':query['created_day']},{'made_user':query['made_user']}]}):
            users.append(member)
        
        keys=connections.twitter_api_keys()
        keys.get_existing_keys(no_of_keys=1)
        
        api=keys.keys[0].connect_to_twitter()
        
        
        for member in users:
            
            new_user=User()
            new_user.make_new_user(member,api)
            
            self.users.append(new_user)
    
    def push_to_community(self):

        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()        
        
        
        for user in self.users:
            
            user_json=user.make_user_json()
            
            if not mongo_app.db.community.find({'user':user_json['user']}).count()>0:
                mongo_app.db.community.insert(user_json)
    
    def get_users(self,query):
        
        mongo_app=connections.mongo()
        mongo_app.connect_to_mongo()
        
        for user in mongo_app.db.community.find(query):
            
            existing_user=User()
            existing_user.make_user(user)
            
            self.users.append(existing_user)
            self.user_ids.append(user['_id'])
            
        
        
        



        
        
        
        