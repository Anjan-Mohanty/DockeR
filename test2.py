import pymongo
import datetime
#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

tweet=db.tweets.find({'user.screen_name':'MKBHD'})

for i in db.tweets.find({'user.screen_name':'MKBHD'}):
    tweet=i
    break

a=[{'name':'1','action':None,'core_user':None},
   {'name':'2','action':None,'core_user':None},
   {'name':'3','action':None,'core_user':None},
   {'name':'4','action':None,'core_user':None},
   {'name':'5','action':None,'core_user':None},
   {'name':'6','action':None,'core_user':None},
   {'name':'7','action':None,'core_user':None},
   {'name':'8','action':None,'core_user':None},
   {'name':'9','action':None,'core_user':None},
   {'name':'10','action':None,'core_user':None}]

import pandas as pd

pd.DataFrame(a,columns=['Name','Action','Cre'])


try:
    db.emp.remove({})
except:
    print('Did not do')

for i in a:
    db.emp.insert(i)

a=[1,2,3,3,4,5,6,2,1]

b=[5,6,7,8]


c=a+b

from collections import Counter

counts=Counter(c)

counts.pop(3)

need=[]
for k,v in counts.items():
    
    temp={}
    
    temp['name']=k
    temp['count']=v
    
    need.append(temp)

need=need[:4]

#today
today=datetime.date.today()
days=7
#setting time period
todaydt=datetime.datetime(today.year,today.month,today.day,0,0,0)
startDate=todaydt-datetime.timedelta(days=days)
endDate=todaydt-datetime.timedelta(days=2)

x=str(startDate)+' - '+str(endDate)

hour=2
lastDate=endDate
query={
       'report':'data_collection',
       'scheduled_hour':hour,
       'last_day':{'scheduler':int(lastDate.strftime('%j')),'add':int(lastDate.strftime('%j')),'discover':int(lastDate.strftime('%j'))},
       'year':{'scheduler':int(lastDate.year),'add':int(lastDate.year),'discover':int(lastDate.year)},
       'tweets_status':{'scheduler':'collected','add':'collected','discover':'collected'},
       'user_friends_status':{'scheduler':'collected','add':'collected','discover':'collected'},
       'tweets_user':{'scheduler':'','add':'','discover':''},
       'friends_user':{'screen_name':'','user_no':0,'type':'old'},
       'duration':{'scheduler':'','add':'','discover':''},
       'quantity':{'scheduler':0,'add':0,'discover':0}
       }

import pandas as pd



x=[query['duration'],query['last_day'],query['quantity'],query['tweets_status'],query['tweets_user'],query['user_friends_status'],query['year']]

df=pd.DataFrame(x,index=['duration','last_day','quantity','tweets_status','tweets_user','user_friends_status','year'])


a=[{'ax':5,'bx':2,'sx':45},{'ax':3,'bx':3,'sx':4},{'ax':4,'bx':27,'sx':5},{'ax':4,'bx':3,'sx':4}]

max(a)
a[max(a)]

a=[1,2,2,3,5]
list(set(a))

pd.DataFrame(a)

y=pd.DataFrame(a)

for i in range(len(y)):
    print(y.iloc[i]['ax'])
    

len(y)
