#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
from datetime import datetime

# ================= CONFIGURATION =================
PING_TARGET = "8.8.8.8"  # Google DNS (tu peux mettre 1.1.1.1 si tu préfères)
CHECK_INTERVAL = 300  # 300 secondes = 5 minutes
DISCORD_WEBHOOK = "WEBHOOK"
STATE_FILE = "/tmp/connection_monitor_state.txt"
# =================================================


def is_connected():
    """Teste la connexion en pingant la cible."""
    try:
        result = subprocess.run(
            ["ping", "-c", "4", PING_TARGET],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Erreur ping : {e}")
        return False


def send_discord_webhook(start_time, end_time):
    """Envoie un embed Discord avec les infos de panne."""
    try:
        duration = end_time - start_time
        duration_seconds = int(duration.total_seconds())
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60

        embed = {
            "title": "Connexion internet rétablie !",
            "color": 5763719,  # vert
            "fields": [
                {
                    "name": "Durée de la panne",
                    "value": f"{minutes} minutes et {seconds} secondes",
                    "inline": False
                },
                {
                    "name": "Heure de début",
                    "value": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                },
                {
                    "name": "Heure de fin",
                    "value": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Raspberry Pi - Monitoring Internet"
            }
        }

        response = requests.post(
            DISCORD_WEBHOOK,
            json={"embeds": [embed]},
            timeout=10
        )

        if response.status_code not in (200, 204):
            print(f"Erreur webhook Discord : {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erreur envoi Discord : {e}")


def save_outage_start(start_time):
    with open(STATE_FILE, "w") as f:
        f.write(start_time.isoformat())


def load_outage_start():
    try:
        with open(STATE_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    except:
        return None


def clear_outage_state():
    try:
        open(STATE_FILE, "w").close()
    except:
        pass


def main():
    print("🔍 Surveillance de la connexion démarrée...")
    outage_start = load_outage_start()

    while True:
        connected = is_connected()

        if not connected:
            if outage_start is None:
                outage_start = datetime.now()
                save_outage_start(outage_start)
                print(f"❌ Connexion perdue à {outage_start}")
        else:
            if outage_start is not None:
                end_time = datetime.now()
                print(f"✅ Connexion rétablie à {end_time}")
                send_discord_webhook(outage_start, end_time)
                outage_start = None
                clear_outage_state()

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()