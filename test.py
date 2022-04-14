from requests import post

req = 'http://127.0.0.1:5000/api/user_add'
# json={'user': 1, 'nomer': 888}
asd = post(req, json={'name': 'artur', 'nomer': '888'})
res = asd.json()
print(res['answer'])
