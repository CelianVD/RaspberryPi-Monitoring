# RaspberryPi-Monitoring

Scripts Python pour surveiller votre Raspberry Pi et recevoir des notifications sur Discord :
- démarrage / arrêt du Raspberry Pi
- nouvelles connexions SSH/SFTP
- coupures et rétablissements de connexion internet (avec durée de la panne)
- 
> [!NOTE]
> Ce bot est destiné à un Raspberry Pi mais peut fonctionner sur n'importe quel serveur.

## Prérequis

- Un Raspberry Pi avec Python 3 installé
- Un webhook Discord (voir ci-dessous comment en créer un)

## 1. Créer un webhook Discord

1. Sur votre serveur Discord, allez dans **Paramètres du salon** > **Intégrations** > **Webhooks**
2. Cliquez sur **Nouveau webhook**, donnez-lui un nom (ex. `Statut Pi`)
3. Copiez l'**URL du webhook**

## 2. Installation

```bash
git clone https://github.com/CelianVD/RaspberryPi-Monitoring.git
cd RaspberryPi-Monitoring
pip install requests
```

## 3. Configuration

Dans chaque script (`on_boot.py`, `on_shutdown.py`, `monitor-login.py`, `internet.py`), remplacez la valeur `"WEBHOOK"` par l'URL de votre webhook Discord :

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/VOTRE_ID/VOTRE_TOKEN"
```

## 4. Utilisation

### Notification au démarrage / à l'arrêt

Ces scripts (`on_boot.py`, `on_shutdown.py`) sont conçus pour être exécutés automatiquement par systemd.

Créez un service systemd, par exemple `/etc/systemd/system/pi-status.service` :

```ini
[Unit]
Description=Notification Discord au démarrage/arrêt du Pi
DefaultDependencies=no
After=network-online.target
Wants=network-online.target
Before=shutdown.target reboot.target halt.target

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/usr/bin/python3 /home/pi/RaspberryPi-Monitoring/on_boot.py
ExecStop=/usr/bin/python3 /home/pi/RaspberryPi-Monitoring/on_shutdown.py

[Install]
WantedBy=multi-user.target
```

Puis activez-le :

```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-status.service
```

### Surveillance des connexions SSH/SFTP

`monitor-login.py` surveille en continu les logs système (`journalctl -u ssh`) et notifie chaque connexion SSH/SFTP détectée.

Lancez-le en tâche de fond, par exemple avec un service systemd :

```ini
[Unit]
Description=Surveillance des connexions SSH
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/RaspberryPi-Monitoring/monitor-login.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now monitor-login.service
```

> Nécessite les droits pour lire les logs `journalctl` (généralement root ou membre du groupe `systemd-journal`).

### Surveillance de la connexion internet

`internet.py` ping `8.8.8.8` toutes les 5 minutes (configurable) et envoie une notification Discord quand la connexion revient, avec la durée de la coupure.

```bash
python3 internet.py
```

Ou en service systemd pour qu'il démarre automatiquement et redémarre en cas de crash :

```ini
[Unit]
Description=Surveillance de la connexion internet
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/RaspberryPi-Monitoring/internet.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now internet-monitor.service
```

## Personnalisation

- **Cible de ping** : modifiez `PING_TARGET` dans `internet.py` (ex. `1.1.1.1`)
- **Intervalle de vérification** : modifiez `CHECK_INTERVAL` (en secondes) dans `internet.py`

## Licence

MIT — voir [LICENSE](LICENSE)
