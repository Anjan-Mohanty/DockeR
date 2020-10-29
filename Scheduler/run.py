import time
import datetime
from Objects import connections
import requests

def main():
    
    mongo_app=connections.mongo()
    mongo_app.connect_to_mongo()
    
    iteration=0
    
    while True:
        
        time.sleep(60*30)
        
        hour=int(datetime.datetime.now().hour)
        day=int(datetime.datetime.now().strftime('%j'))
        
        reports=[]
        for report in mongo_app.db.reports.find({'report':'data_collection'}):
            reports.append(report)
        
        if len(reports)!=0:
            
            if((reports[0]['last_day']['scheduler']!=day) and (reports[0]['scheduled_hour']<hour)):
                
                session = requests.Session()
                session.trust_env = False
                
                user_query={}
                
                lastDate=datetime.datetime(reports[0]['year']['scheduler'], 1, 1) + datetime.timedelta(reports[0]['last_day']['scheduler'] - 1)
                days=datetime.datetime.now()-lastDate
                
                if days.days+2>=7:
                    days=7
                else:
                    days=days.days+2
                
                tweets_payload={'days':days,'user_payload':user_query,'source':'scheduler'}
                url="http://datacollection:5010/tweets"
                
                report= session.post(url,json=tweets_payload)
                
                time.sleep(5)
                
                user_friends_query={}
                user_payload={'type':'old','user_friends_payload':user_friends_query,'source':'scheduler'}
                url="http://datacollection:5010/user_friends"
                
                report= session.post(url,json=user_payload)
                
                today=datetime.datetime.now()
                month_back=today-datetime.timedelta(days=30)
                
                month_back_day=month_back.strftime('%j')
                month_back_year=month_back.year
                
                mongo_app.db.tweets.remove({'created_year':month_back_year-1})
                
                mongo_app.db.tweets.remove({'$and':[{'created_year':month_back_year},{'created_day':{'$lt':month_back_day}}]})
            
            elif iteration!=0:
                
                try:
                    
                    if((reports[0]['last_day']['scheduler']==day) and (reports[0]['tweets_status']['scheduler']=='collecting') and (reports[0]['tweets_user']['scheduler']==old_user_tweets)):
                        

                        url="http://datacollection:5010/tweets"
                
                        report= session.post(url,json=tweets_payload)
                
                    if((reports[0]['last_day']['scheduler']==day) and (reports[0]['user_friends_status']['scheduler']=='collecting') and (reports[0]['friends_user']['screen_name']==old_user_friends)):
                        
                        
                        url="http://datacollection:5010/user_friends"
                
                        report= session.post(url,json=user_payload)
                    
                except Exception as e:
                    pass
                
            old_user_tweets=reports[0]['tweets_user']['scheduler']
            old_user_friends=reports[0]['friends_user']['screen_name']
            iteration+=1
                


if __name__=='__main__':
    main()
    

#print(datetime.datetime.now().hour)
#print(datetime.datetime.now().strftime('%j'))