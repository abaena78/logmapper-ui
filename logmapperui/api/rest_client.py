# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 09:11:01 2018

@author: abaena
"""

import requests

from requests.auth import HTTPBasicAuth


import json



#d={"header" : { "userId" : "1", "apiTraceId" : "45635656437"}}
#js=json.dumps(d)
#
#headers = {'Content-type': 'application/json', 'Accept-Encoding': 'gzip,deflate', "Content-Length" : "60"} # 'Accept': 'text/plain'  charset=utf-8
#headers = {'Content-type': 'application/json'} # 'Accept': 'text/plain'  charset=utf-8
#
#
#resp = requests.post('http://localhost:4016/findAllCity', auth=HTTPBasicAuth('location', 'osp123'), headers=headers, json=js)
#print(str(resp))
#if resp.status_code != 200:
#    print("Error:"+'GET /tasks/ {}'.format(resp.status_code))
#else:
#    for todo_item in resp.json():
#        print(str(todo_item))



d={"data" : { "userId" : "1", "apiTraceId" : "45635656437"}}
js=json.dumps(d)

headers = {'Content-type': 'application/json', 'Accept-Encoding': 'gzip,deflate', "Content-Length" : "60"} # 'Accept': 'text/plain'  charset=utf-8
headers = {'Content-type': 'application/json'} # 'Accept': 'text/plain'  charset=utf-8


resp = requests.post('http://localhost:5005/get/test', headers=headers, json=js)
print(str(resp))
if resp.status_code != 200:
    print("Error:"+'GET /tasks/ {}'.format(resp.status_code))
else:
    print(str(resp.json()))





#resp = requests.get('http://localhost:5005/get/ccococ')
#print(str(resp)+":"+str(resp.text) )