import requests

url='http://localhost:5000/'
payload={'hi':1}
response=requests.post(url,json=payload)

print(response.text)