from app import app
from flask import request
from app import tasks

#tweets collection
@app.route('/tweets',methods=['POST','GET'])
def tweets_collector():
    
    query=dict(request.get_json())
    tasks.tweets_celery_collector.delay(query)
    
    return 'done'

#user_friends collection
@app.route('/user_friends',methods=['POST','GET'])
def user_friends_collector():
    
    query=dict(request.get_json())
    tasks.user_friends_celery_collector.delay(query)
    
    return 'done'
