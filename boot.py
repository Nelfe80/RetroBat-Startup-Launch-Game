import os
import time
import subprocess
import psutil
import xml.etree.ElementTree as ET
import requests
import configparser
import shutil

# === Définition du répertoire de base ===
# On suppose que le répertoire de travail courant est celui où se trouvent boot.exe et boot.ini
base_dir = os.getcwd()

# === Suppression des dossiers dans .tmp sauf le plus récent ===
tmp_dir = os.path.join(base_dir, ".tmp")
if os.path.exists(tmp_dir):
    # Liste uniquement les dossiers présents dans .tmp
    directories = [os.path.join(tmp_dir, d) for d in os.listdir(tmp_dir)
                   if os.path.isdir(os.path.join(tmp_dir, d))]
    if directories:
        # Sélectionne le dossier le plus récent (basé sur le temps de modification)
        latest_dir = max(directories, key=os.path.getmtime)
        for d in directories:
            if d != latest_dir:
                print(f"Suppression du dossier : {d}")
                shutil.rmtree(d)
else:
    print(f"Le dossier .tmp n'existe pas à {tmp_dir}")

# === 1. Lecture du fichier boot.ini avec configparser ===
boot_ini_path = os.path.join(base_dir, "boot.ini")

if not os.path.exists(boot_ini_path):
    print("Erreur : boot.ini introuvable.")
    exit(1)

boot = configparser.ConfigParser()
boot.read(boot_ini_path, encoding="utf-8")

try:
    # Lecture des options dans la section [Default]
    bootrom = boot.get("Default", "bootrom")
    bootcommand = boot.get("Default", "bootcommand")
except configparser.Error as e:
    print("Erreur lors de la lecture de boot.ini :", e)
    exit(1)

# Convertir les chemins relatifs en chemins absolus si nécessaire
if not os.path.isabs(bootrom):
    bootrom = os.path.join(base_dir, bootrom)
if not os.path.isabs(bootcommand):
    bootcommand = os.path.join(base_dir, bootcommand)

# === 2. Modification de es_settings.cfg ===
# Le script est dans C:/RetroBatV7/plugins/StartupLaunchGame/
# et es_settings.cfg se trouve dans C:/RetroBatV7/emulationstation/.emulationstation/
es_cfg_dir = os.path.normpath(os.path.join(base_dir, "../../emulationstation/.emulationstation"))
es_cfg_path = os.path.join(es_cfg_dir, "es_settings.cfg")

# Vérifie que le dossier de configuration existe, sinon le crée
if not os.path.exists(es_cfg_dir):
    os.makedirs(es_cfg_dir)

# Tente de charger le fichier XML, sinon en créer un nouveau document
if os.path.exists(es_cfg_path) and os.path.getsize(es_cfg_path) > 0:
    try:
        tree = ET.parse(es_cfg_path)
        root = tree.getroot()
    except ET.ParseError:
        print("Fichier es_settings.cfg invalide, création d'un nouveau fichier.")
        root = ET.Element("config")
        tree = ET.ElementTree(root)
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
# Pour que le batch trouve ses fichiers, on définit le répertoire de travail à celui du batch.
# On récupère le dossier du batch en le séparant de son nom de fichier.
start_bat_dir = bootcommand.rsplit(os.sep, 1)[0]
subprocess.Popen(bootcommand, shell=True, cwd=start_bat_dir)

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
