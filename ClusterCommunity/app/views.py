from app import app
from flask import request
import igraph as ig
from Objects import connections,user_objects



@app.route('/',methods=['POST','GET'])
def index():
    
    query=dict(request.get_json())
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    all_users=user_objects.user_set()
    all_users.get_users({})
    
    #making empty graph
    g=ig.Graph(directed=True)
    
    #making vertices
    for user in all_users.users:
        g.add_vertex(name=user.user['screen_name'],size=user.activity)
    
    #making edges
    for user in all_users.users:
        for edge in user.edges:
            if edge['bond']!=0:
                g.add_edge(user.user['screen_name'],edge['screen_name'],weight=edge['bond'])
    
    #clustering people
    cluster=g.community_infomap(edge_weights=g.es['weight'],vertex_weights=g.vs['size'],trials=1000)
    
    cluster_number=0
    for graph in cluster.subgraphs():
        
        for vertex in graph.vs:
            mongo_app.db.community.update({'user.screen_name':vertex['name']},{'$set':{'cluster_number':cluster_number}})
        
        cluster_number+=1
    
    if mongo_app.db.reports.find({'report':'cluster_community'}).count()>0:
        
        mongo_app.db.reports.update({'report':'cluster_community'},{'$set':{'no_users':len(all_users.users),'no_clusters':cluster_number}})
    
    else:
        mongo_app.db.reports.insert({'report':'cluster_community','no_users':len(all_users.users),'no_clusters':cluster_number})

    return('done')