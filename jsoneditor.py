import requests
import jsoneditor

data = requests.get('https://jsonplaceholder.typicode.com/comments').json()
jsoneditor.editjson(data)
