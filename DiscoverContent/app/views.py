from app.celery import celery_app as celery_app
from app import app as app
from flask import request
from app import tasks
from Objects import connections
import time
import random

@app.route('/',methods=['POST','GET'])
def index():
    
    query=dict(request.get_json())
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    for i in mongo_app.db.reports.find({'report':'cluster_community'}):
        no_clusters=i['no_clusters']
        break
    
    results=[]
    results_count=no_clusters
    
    for cluster_number in range(no_clusters):
        
        query={'cluster_number':cluster_number}
        
        result=tasks.discover.delay(query)
        t=random.uniform(0,3)
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
        