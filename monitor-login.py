import re
import subprocess

from datetime import datetime
import requests

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "WEBHOOK"


def send_discord_notification(user, service):
  now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

  payload = {
      "embeds": [{
          "title": "🚨 Nouvelle Connexion Détectée",
          "color": 3447003,  # Bleu
          "fields": [
              {"name": "Utilisateur", "value": f"`{user}`", "inline": True},
              {"name": "Service", "value": f"**{service}**", "inline": True},
              {"name": "Date et Heure", "value": now, "inline": False},
          ],
          "footer": {"text": "Raspberry Pi Monitor"},
      }]
  }

  try:
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
  except Exception as e:
    print(f"Erreur d'envoi Discord : {e}")


def watch_logs():
  cmd = ["journalctl", "-u", "ssh", "-f", "-n", "0"]
  process = subprocess.Popen(
      cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
  )

  print("Surveillance du journal système (SSH/SFTP) démarrée...")

  for line in process.stdout:
    if "Accepted" in line or "session opened" in line:
      user_match = re.search(r"for (\S+)", line)

      user = user_match.group(1) if user_match else "Inconnu"
      service = "SFTP" if "subsystem sftp" in line.lower() else "SSH"

      send_discord_notification(user, service)


if __name__ == "__main__":
  watch_logs()
