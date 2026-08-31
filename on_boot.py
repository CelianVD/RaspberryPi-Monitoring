import requests
url = "WEBHOOK"
data = {"content": "🚀 **Le Raspberry Pi vient de démarrer !**", "username": "Statut Pi"}
requests.post(url, json=data)