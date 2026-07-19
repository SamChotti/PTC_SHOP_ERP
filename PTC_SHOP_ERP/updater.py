import requests
import os
import sys
import subprocess
import tempfile
from PySide6.QtWidgets import QMessageBox

CURRENT_VERSION = "1.0.3" # Release tag number. v1.0.4 panna idhuvum maathanum
GITHUB_REPO = "SamChotti/PTC_SHOP_ERP"

def check_for_update(parent):
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        latest_data = r.json()

        latest_version = latest_data["tag_name"] # v1.0.3
        download_url = latest_data["assets"][0]["browser_download_url"]

        latest_num = latest_version.replace("v","")
        if latest_num > CURRENT_VERSION:
            reply = QMessageBox.question(parent, 'Update Available',
                f'New Version {latest_version} Available\nCurrent: v{CURRENT_VERSION}\n\nDownload & Restart Now?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                download_and_install(parent, download_url)
    except Exception as e:
        print("Update check failed:", e) # internet illa na idhu varum

def download_and_install(parent, url):
    QMessageBox.information(parent, "Updating", "Downloading update... App will restart in 3 sec")
    r = requests.get(url)
    temp_exe = os.path.join(tempfile.gettempdir(), "PTC_ERP_Update.exe")
    with open(temp_exe, "wb") as f:
        f.write(r.content)

    current_exe = sys.executable
    bat_file = os.path.join(tempfile.gettempdir(), "update.bat")
    with open(bat_file, "w") as f:
        f.write(f'@echo off\ntimeout /t 3\nmove /Y "{temp_exe}" "{current_exe}"\nstart "" "{current_exe}"\ndel "%~f0"')

    subprocess.Popen([bat_file], shell=True)
    sys.exit()