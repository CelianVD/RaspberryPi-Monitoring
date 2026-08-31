import requests
url = "WEBHOOK"
data = {"content": "🛑 **Le Raspberry Pi s'éteint...**", "username": "Statut Pi"}
requests.post(url, json=data)