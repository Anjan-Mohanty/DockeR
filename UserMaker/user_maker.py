from flask import Flask,request
import user_objects

backend_micro_app=Flask(__name__)


@backend_micro_app.route('/',methods=['GET','POST'])
def user_maker():
    query=request.get_json()
    
    #users=user_objects.user_set()
    #users.make_new_users(query)
    #users.push_to_community()
    return '^_^'
    

if __name__=='__main__':
    backend_micro_app.run(port=5000)