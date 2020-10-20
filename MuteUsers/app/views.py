from app import app
from flask import request
from Objects import connections


@app.route('/',methods=['POST','GET'])
def index():
    
    query=dict(request.get_json())
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    try:
        
        mongo_app.db.mute.update_many({'status':'Mute'},{'$inc':{'activity':-1}})
        
        mongo_app.db.mute.remove({'$and':[{'status':'Mute'},{'activity':0}]})
        
    except:
        pass
    
    query={'$and':[{'made_user':False},{'$or':[{'status':'Mute'},{'status':'Block'}]}]}
    
    mute_users=[]
    for user in mongo_app.db.users.find(query):
        
        mute_users.append(user)
    
    for user in mute_users:
        
        user['activity']=7
        mongo_app.db.users.update({'_id':user['_id']},{'made_user':True})
        user.pop('_id')
        mongo_app.db.mute.insert(user)
    
    
    return('done')