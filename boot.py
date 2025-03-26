import os
import time
import subprocess
import psutil
import xml.etree.ElementTree as ET
import requests

# === Base du dossier du script de base ===
base_dir = os.path.dirname(os.path.abspath(__file__))

# === 1. Lecture du fichier boot.ini ===
boot_ini_path = os.path.join(base_dir, "boot.ini")
bootrom = None
bootcommand = None

if not os.path.exists(boot_ini_path):
    print("Erreur : boot.ini introuvable.")
    exit(1)

with open(boot_ini_path, "r", encoding="utf-8") as f:
    for line in f:
        if "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if key.lower() == "bootrom":
                bootrom = os.path.join(base_dir, value) if not os.path.isabs(value) else value
            elif key.lower() == "bootcommand":
                bootcommand = os.path.join(base_dir, value) if not os.path.isabs(value) else value

if not bootrom or not bootcommand:
    print("Erreur : bootrom ou bootcommand non défini dans boot.ini.")
    exit(1)

# === 2. Modification de es_settings.cfg ===
user_home = os.path.expanduser("~")
es_cfg_dir = os.path.join(user_home, ".emulationstation")
es_cfg_path = os.path.join(es_cfg_dir, "es_settings.cfg")

if not os.path.exists(es_cfg_dir):
    os.makedirs(es_cfg_dir)

if os.path.exists(es_cfg_path):
    tree = ET.parse(es_cfg_path)
    root = tree.getroot()
else:
    root = ET.Element("config")
    tree = ET.ElementTree(root)

# Ajoute ou met à jour l'entrée PublicWebAccess
found = False
for e in root.findall("bool"):
    if e.attrib.get("name") == "PublicWebAccess":
        e.attrib["value"] = "true"
        found = True
if not found:
    ET.SubElement(root, "bool", name="PublicWebAccess", value="true")

tree.write(es_cfg_path)

# === 3. Lancement de bootcommand ===
print(f"Lancement de : {bootcommand}")
subprocess.Popen(bootcommand, shell=True)

# === 4. Attente de emulationstation.exe ===
print("Recherche de emulationstation.exe...")

while True:
    if any("emulationstation.exe" in (p.info["name"] or "").lower() for p in psutil.process_iter(['name'])):
        break
    time.sleep(1)

print("emulationstation.exe détecté. Attente du serveur HTTP...")

# === 5. Attente de l'API HTTP locale ===
url = "http://127.0.0.1:1234"
while True:
    try:
        r = requests.get(url, timeout=1)
        if r.status_code == 200:
            break
    except requests.exceptions.RequestException:
        pass
    time.sleep(1)

print("API EmulationStation disponible.")

# === 6. Envoi de la requête HTTP POST ===
print(f"Lancement du jeu : {bootrom}")
try:
    response = requests.post(
        f"{url}/launch",
        data=bootrom,
        headers={"Content-Type": "text/plain"}
    )
    print("Jeu lancé. Code HTTP :", response.status_code)
except Exception as e:
    print("Erreur lors de la requête POST :", e)
