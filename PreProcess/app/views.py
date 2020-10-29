from app.celery import celery_app
from app import app
from flask import request
from app import tasks
from Objects import connections
from Objects import user_objects
import time
import random

@app.route('/',methods=['POST','GET'])
def index():
    
    query=dict(request.get_json())
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
            
    reports=[]
    for i in mongo_app.db.reports.find({'report':'preprocess'}):
        reports.append(i)
        
    all_users=user_objects.user_set()
    all_users.get_users({})
    
    results=[]
    results_count=len(all_users.users)
    
    for user in all_users.users:
        
        query={}
        query['user']=user.user['screen_name']
        query['weights']={'tweet_weight':reports[0]['tweet_weight'],'tweet_mention_weight':reports[0]['tweet_mention_weight'],'retweet_weight':reports[0]['retweet_weight'],'quote_weight':reports[0]['quote_weight'],'reply_weight':reports[0]['reply_weight']}
        
        
        result=tasks.process.delay(query)
        t=random.uniform(0,2)
        print(t)#only for debug purpose 
        time.sleep(t)
        results.append(result)
    
    success_count=0
    while(success_count==results_count):
        
        success_count=0
        for result in results:
            if result.status=='SUCCESS':
                success_count+=1
    
    
    
    return 'done'

