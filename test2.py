import tweepy

#getting to twitter api info
auth_path='E:/twitter_data/discover_weekly_data&report/auth.txt'

with open(auth_path,'r') as f:
    auth=f.read()

auth=auth.split(';')

for i in range(len(auth)):
    auth[i]=auth[i].split(',')

auth_no=int(input('Enter Auth number : '))

auth_details=tweepy.OAuthHandler('26','51')
auth_details.set_access_token('251','151')

api=tweepy.API(auth_details,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

users=['MKBHD','SuperSaf','indie_tat']

i=2

try:
    new_user=api.get_user(id=users[i])
except Exception as e:
    
    if e.reason[:22]=='Failed to send request':
        print('failed')
    
    print(e.api_code)
    
try:
    new_user=api.get_user(id='pkkt')
except tweepy.TweepError:
    
    y=tweepy.TweepError
    print(y.api_code)
    
[{'code': 50, 'message': 'User not found.'}]

x.reason.split(':')[0]=='Failed to send request'
