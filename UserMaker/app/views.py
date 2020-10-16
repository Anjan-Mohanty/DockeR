from app import app
from flask import request
from Objects import user_objects

@app.route('/',methods=['POST','GET'])
def index():
    query=dict(request.get_json())
    
    users=user_objects.user_set()
    users.make_new_users(query)
    users.push_to_community()
    return ' 🐱‍💻'