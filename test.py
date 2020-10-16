import requests

payload={}
url="http://localhost:5010/tweets"
                
session = requests.Session()
session.trust_env = False

for i in range(10):               
    report= session.post(url,json=payload)
    

a=1
b=0

try:
    
    #d=a[0]
    c=a/b
    print(c)
except TypeError:
    print('not possible')
except:
    print('something happend')
