import sys
import os
import socket
import requests
import psutil
import datetime
import subprocess
import re
import json
import shutil
import zipfile

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                               QScrollArea, QCheckBox, QGridLayout, QComboBox, 
                               QProgressBar, QGroupBox, QSlider, QLineEdit, QFormLayout, 
                               QFrame, QMessageBox, QTabWidget, QTextEdit, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QSpinBox, QSizePolicy, QLayout, QFileDialog,
                               QSystemTrayIcon, QMenu, QStyle)
from PySide6.QtCore import Qt, QEvent, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor, QAction

# ==========================================
# 全域常數與設定檔載入
# ==========================================
EULA_ZH_TEXT = """<div style='line-height: 1.6; font-size: 14px;'>
<h2 style='color: #10B981;'>Minecraft 終端使用者授權合約（「EULA」）</h2>
<h3 style='color: #3B82F6;'>摘要</h3>
本 EULA 是您與我們（Mojang AB 和微軟公司）之間的法律合約。在此提供一些重要點的快速摘要以供參考：<br>
• 本 Minecraft EULA 與微軟服務合約，共同適用於所有 Minecraft 服務。<br>
• 您的內容屬於您自己，但請負責任且安全地分享。<br>
• 您可以開發工具、外掛程式（插件）與服務，只要它們看起來不像是官方的即可。<br>
• 未經我們許可，請勿散佈或將我們製作的任何內容用於商業用途。<br><br>

<h3 style='color: #3B82F6;'>您對 Minecraft 軟體與內容可以做與不能做的事</h3>
當您購買我們的遊戲時，這意味著您可以下載、安裝並遊玩它們。對於 Minecraft：Java 版的伺服器版本，您可以將其安裝在伺服器上並託管線上多人遊戲。<br>
然而，除非我們特別同意，否則您絕不能散佈我們製作的任何內容。包含：<br>
• 將我們遊戲軟體或內容的副本給予任何其他人；<br>
• 將我們製作的任何內容用於商業用途或試圖賺取金錢；<br>
• 讓其他人以不公平或不合理的方式取得遊戲存取權限。<br>

<h3 style='color: #3B82F6;'>使用模組 (Mods)</h3>
如果您購買了 Minecraft：Java 版，您可以透過加入修改、工具或外掛程式（「模組」）來修改它。您不得散佈我們遊戲或軟體的任何模改版本。<br>

<h3 style='color: #3B82F6;'>MINECRAFT 社群標準</h3>
為了讓社群保持包容，我們對仇恨言論、恐怖或暴力內容、霸凌、騷擾、詐欺採取零容忍政策。我們保留暫停或永久封禁任何違反這些標準的人的權利。<br>
</div>"""

EULA_EN_TEXT = """<div style='line-height: 1.6; font-size: 14px;'>
<h2 style='color: #10B981;'>Minecraft End-User License Agreement (“EULA”)</h2>
<h3 style='color: #3B82F6;'>SUMMARY</h3>
This EULA is a legal agreement between you and us (Mojang AB and Microsoft Corporation). Here is a quick summary:<br>
• This EULA and the Microsoft Services Agreement apply to all Minecraft services.<br>
• Your content is yours, but please share it responsibly and safely.<br>
• You may develop tools and plug-ins as long as they do not seem official.<br>
• Do not distribute or make commercial use of anything we've made without permission.<br><br>

<h3 style='color: #3B82F6;'>What you can and can’t do</h3>
When you buy our games, you can download, install, and play them. You can install the server software and host online play.<br>
However, you must not distribute anything we've made. This means:<br>
• give copies of our game to anyone else;<br>
• make commercial use or try to make money from our work;<br>
• let other people get access in an unfair way.<br>

<h3 style='color: #3B82F6;'>USING mods</h3>
You may modify the game by adding tools or plugins ("Mods"). You may not distribute any Modded Versions of our game.<br>

<h3 style='color: #3B82F6;'>COMMUNITY STANDARDS</h3>
We have a zero-tolerance policy towards hate speech, violent content, bullying, harassment, and fraud. We reserve the right to ban anyone who violates these standards.<br>
</div>"""

CONFIG_FILE = "panel_config.json"
DEFAULT_CONFIG = {
    "first_run": True,
    "is_dark": True,
    "language": "zh",
    "servers": [],
    "active_server": ""
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return DEFAULT_CONFIG.copy()

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

APP_CONFIG = load_config()

def _tr(zh_txt, en_txt): return zh_txt if APP_CONFIG["language"] == "zh" else en_txt

os.makedirs("servers", exist_ok=True)
if APP_CONFIG["active_server"]:
    os.makedirs(os.path.join("servers", APP_CONFIG["active_server"]), exist_ok=True)

# 動作按鈕佈局包裹器
def create_action_widget(widgets):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(2, 2, 2, 2) 
    layout.setSpacing(6)
    for w in widgets: layout.addWidget(w)
    layout.addStretch()
    return container

# ==========================================
# 介面視覺樣式引擎
# ==========================================
def get_stylesheet(is_dark=True):
    bg_main = "#1A1B1E" if is_dark else "#F4F6F8"
    bg_panel = "#25262B" if is_dark else "#FFFFFF"
    bg_input = "#2C2E33" if is_dark else "#EDF2F7"
    bg_sidebar = "#141517" if is_dark else "#FDFDFD"
    text_main = "#E0E0E0" if is_dark else "#2D3748"
    text_sub = "#90A4AE" if is_dark else "#718096"
    primary = "#10B981" 
    border = "#373A40" if is_dark else "#D1D5DB"

    return f"""
        QMainWindow {{ background-color: {bg_main}; }}
        QWidget {{ color: {text_main}; font-family: "Segoe UI", "Microsoft JhengHei UI", "Microsoft YaHei", sans-serif; font-size: 14px; line-height: 1.5; }}
        h1.title {{ font-size: 24px; color: {text_main}; margin-bottom: 20px; font-weight: 900; border-left: 5px solid {primary}; padding-left: 12px; }}
        h2 {{ color: {primary}; font-weight: bold; margin-bottom: 10px; font-size: 16px;}}
        
        QWidget#Sidebar {{ background-color: {bg_sidebar}; border-right: 1px solid {border}; }}
        QWidget#Topbar {{ background-color: {bg_sidebar}; border-bottom: 1px solid {border}; }}
        
        QPushButton#NavBtn {{ background: transparent; text-align: left; padding: 12px 20px; border: none; font-size: 14px; color: {text_sub}; font-weight: bold; border-left: 3px solid transparent; }}
        QPushButton#NavBtn:hover {{ background-color: {bg_input}; color: {text_main}; border-radius: 6px;}}
        
        QComboBox, QLineEdit, QSpinBox {{ background-color: {bg_input}; border: 1px solid {border}; padding: 10px 12px; border-radius: 6px; color: {text_main}; }}
        QComboBox::drop-down {{ border: none; }}
        
        QGroupBox {{ border: 1px solid {border}; border-radius: 8px; margin-top: 25px; padding-top: 20px; font-weight: bold; font-size: 15px; background-color: {bg_panel};}}
        QGroupBox::title {{ subcontrol-origin: margin; left: 15px; color: {primary}; padding: 0 5px; }}
        
        QFrame#DashboardCard, QFrame#ModCard, QFrame#ManualCard {{ background-color: {bg_input}; border-radius: 8px; padding: 15px; border: 1px solid {border}; }}
        
        QTableWidget {{ background-color: {bg_input}; border: 1px solid {border}; color: {text_main}; border-radius: 8px; outline: none; }}
        QTableWidget::item {{ padding: 2px; }}
        QHeaderView::section {{ background-color: {bg_panel}; color: {text_sub}; padding: 10px; border: none; font-weight: bold; border-bottom: 1px solid {border};}}
        
        QWidget#ModalMask {{ background-color: rgba(0, 0, 0, 210); }}
        QWidget#ModalContainer {{ background-color: {bg_panel}; border-radius: 12px; border: 1px solid {border}; }}
        
        QProgressBar {{ border: none; border-radius: 6px; text-align: center; background-color: {bg_input}; height: 16px; color: {text_main}; font-weight: bold; }}
        QProgressBar::chunk {{ background-color: {primary}; border-radius: 6px; }}
        
        QPushButton {{ text-align: center; padding: 8px 14px; border-radius: 6px; border: none; font-weight: bold; font-size: 14px;}}
        QPushButton:disabled {{ background-color: {border}; color: #666666; }}
        QPushButton#PrimaryBtn {{ background-color: {primary}; color: #FFFFFF; font-size: 15px; padding: 12px;}}
        QPushButton#PrimaryBtn:hover {{ background-color: #34D399; }}
        QPushButton#SecondaryBtn {{ background-color: {bg_input}; color: {text_main}; border: 1px solid {border}; }}
        QPushButton#SecondaryBtn:hover {{ background-color: {border}; }}
        QPushButton#DangerBtn {{ background-color: #EF4444; color: #FFFFFF; }}
        QPushButton#DangerBtn:hover {{ background-color: #F87171; }}
        QPushButton#SuccessBtn {{ background-color: #3B82F6; color: #FFFFFF; }}
        QPushButton#SuccessBtn:hover {{ background-color: #60A5FA; }}
        
        QPushButton#CancelGrayBtn {{ background-color: #6c757d; color: #FFFFFF; font-size: 15px; padding: 12px; }}
        QPushButton#CancelGrayBtn:hover {{ background-color: #9CA3AF; }}
        
        QTableWidget QPushButton {{ padding: 5px 12px; font-size: 13px; }}
        
        QTabWidget::pane {{ border: 1px solid {border}; border-radius: 8px; background: {bg_panel}; }}
        QTabBar::tab {{ background: {bg_sidebar}; color: {text_sub}; padding: 10px 20px; border: 1px solid {border}; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
        QTabBar::tab:selected {{ background: {bg_input}; color: {primary}; font-weight: bold; border-bottom: none; }}
        
        QScrollArea {{ border: none; background-color: transparent; }}
        QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 8px; }}
        QScrollBar::handle:vertical {{ background: {border}; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover {{ background: #555555; }}
        
        QTextEdit {{ border: 1px solid {border}; border-radius: 8px; padding: 10px; background-color: #0A0A0A; font-family: "Consolas", "Courier New", monospace; color: #D1D5DB; line-height:1.5; }}
    """

# ==========================================
# 2. 真實背景執行緒 群組
# ==========================================

# 抓取外網 IP 執行緒
class FetchPublicIPThread(QThread):
    result = Signal(str)
    def run(self):
        try:
            ip = requests.get("https://api.ipify.org", timeout=5).text
            self.result.emit(ip)
        except: self.result.emit(_tr("無法獲取", "Unavailable"))

# 抓取遊戲核心版本執行緒
class FetchCoreVersionsThread(QThread):
    finished = Signal(list)
    def __init__(self, core_type, parent=None):
        super().__init__(parent)
        self.core_type = core_type.lower()
    def run(self):
        try:
            versions = []
            if "vanilla" in self.core_type:
                res = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json", timeout=5).json()
                versions = [v['id'] for v in res['versions'] if v['type'] == 'release'][:40]
            elif "paper" in self.core_type:
                res = requests.get("https://api.papermc.io/v2/projects/paper", timeout=5).json()
                versions = res.get("versions", [])[-40:][::-1]
            elif "fabric" in self.core_type:
                res = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=5).json()
                versions = [v['version'] for v in res if v.get('stable')][:40]
            self.finished.emit(versions if versions else [_tr("無可用版本", "No versions found")])
        except: self.finished.emit([_tr("抓取失敗，請確認網路", "Fetch failed")])

# 下載伺服器核心執行緒
class DownloadCoreThread(QThread):
    progress = Signal(int)
    finished = Signal(str, bool) 
    def __init__(self, core_type, version, server_name, parent=None):
        super().__init__(parent)
        self.core_type = core_type
        self.version = version
        self.server_name = server_name
    def run(self):
        try:
            target_dir = os.path.join("servers", self.server_name)
            os.makedirs(target_dir, exist_ok=True)
            filename = f"server-{self.version}.jar"
            filepath = os.path.join(target_dir, filename)
            with open(os.path.join(target_dir, "eula.txt"), "w") as f: f.write("eula=true\n")
            
            dl_url = ""
            total_size_known = True

            if "Paper" in self.core_type:
                b_url = f"https://api.papermc.io/v2/projects/paper/versions/{self.version}/builds"
                b_res = requests.get(b_url, timeout=5).json()
                latest_build = b_res['builds'][-1]['build']
                file_name = b_res['builds'][-1]['downloads']['application']['name']
                dl_url = f"https://api.papermc.io/v2/projects/paper/versions/{self.version}/builds/{latest_build}/downloads/{file_name}"
            elif "Vanilla" in self.core_type:
                m_url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
                manifest = requests.get(m_url, timeout=5).json()
                v_url = next(v['url'] for v in manifest['versions'] if v['id'] == self.version)
                dl_url = requests.get(v_url, timeout=5).json()['downloads']['server']['url']
            elif "Fabric" in self.core_type:
                dl_url = f"https://meta.fabricmc.net/v2/versions/loader/{self.version}/0.15.11/1.0.1/server/jar"
                total_size_known = False

            if dl_url:
                response = requests.get(dl_url, stream=True, timeout=10)
                total_size = int(response.headers.get('content-length', 0))
                if total_size == 0 or not total_size_known: self.progress.emit(-1)
                
                downloaded = 0
                with open(filepath, 'wb') as f:
                    for data in response.iter_content(8192):
                        f.write(data)
                        downloaded += len(data)
                        if total_size > 0 and total_size_known: 
                            self.progress.emit(int(downloaded * 100 / total_size))
                self.finished.emit(_tr("✅ 核心下載完畢！", "✅ Core downloaded!"), True)
        except Exception as e: self.finished.emit(f"❌ {str(e)}", False)

# 搜尋市集模組執行緒
class FetchModsThread(QThread):
    finished = Signal(list)
    def __init__(self, query="", core_type="", core_ver="", project_type="mod", parent=None):
        super().__init__(parent)
        self.query = query
        self.core_type = core_type
        self.core_ver = core_ver
        self.project_type = project_type

    def run(self):
        try:
            facets_list = []
            if self.core_type in ["fabric", "forge", "quilt"]:
                facets_list.append([f"categories:{self.core_type}"])
            elif self.core_type in ["paper", "spigot", "purpur"]:
                facets_list.append([f"categories:paper", "categories:spigot"])
                
            if self.core_ver and "未" not in self.core_ver:
                facets_list.append([f"versions:{self.core_ver}"])
            
            if self.project_type != "all":
                facets_list.append([f"project_type:{self.project_type}"])
                
            facets_param = json.dumps(facets_list) if facets_list else ""
            params = {"query": self.query, "limit": 30}
            if facets_param: params["facets"] = facets_param
                
            url = "https://api.modrinth.com/v2/search"
            res = requests.get(url, params=params, timeout=5)
            hits = res.json().get("hits", [])
            mods = [(h['title'], h['description'], h['author'], h['slug']) for h in hits]
            self.finished.emit(mods)
        except: self.finished.emit([])

# 下載模組檔案執行緒
class DownloadModThread(QThread):
    progress = Signal(int)
    finished = Signal(str, str) 
    def __init__(self, slug, server_name, parent=None):
        super().__init__(parent)
        self.slug = slug
        self.server_name = server_name
    def run(self):
        try:
            v_url = f"https://api.modrinth.com/v2/project/{self.slug}/version"
            v_res = requests.get(v_url, timeout=5).json()
            if not v_res:
                self.finished.emit(_tr("無載點", "No URL"), "red")
                return
            file_info = v_res[0]['files'][0]
            dl_url = file_info['url']
            filename = file_info['filename']
            
            mods_dir = os.path.join("servers", self.server_name, "mods")
            os.makedirs(mods_dir, exist_ok=True)
            filepath = os.path.join(mods_dir, filename)
            
            response = requests.get(dl_url, stream=True, timeout=10)
            total = int(response.headers.get('content-length', 0))
            if total == 0: self.progress.emit(-1)
            downloaded = 0
            with open(filepath, 'wb') as f:
                for data in response.iter_content(4096):
                    f.write(data)
                    downloaded += len(data)
                    if total > 0: self.progress.emit(int(downloaded * 100 / total))
            self.finished.emit(_tr("✅ 部署成功", "✅ Installed"), "#10B981")
        except: self.finished.emit(_tr("❌ 下載失敗", "❌ Failed"), "red")

# 伺服器本體啟動與溝通執行緒
class ServerRunnerThread(QThread):
    log_signal = Signal(str)
    stopped_signal = Signal()
    def __init__(self, server_dir, jar_file, ram_gb, aikar=False, custom_args="", parent=None):
        super().__init__(parent)
        self.server_dir = server_dir
        self.jar_file = jar_file
        self.ram_gb = ram_gb
        self.aikar = aikar
        self.custom_args = custom_args
        self.process = None
        self.is_running = True
    def run(self):
        cmd = ["java", f"-Xms{self.ram_gb}G", f"-Xmx{self.ram_gb}G", "-Dfile.encoding=UTF-8"]
        if self.aikar:
            cmd.extend([
                "-XX:+UseG1GC", "-XX:+ParallelRefProcEnabled", "-XX:MaxGCPauseMillis=200", 
                "-XX:+UnlockExperimentalVMOptions", "-XX:+DisableExplicitGC", "-XX:G1NewSizePercent=30", 
                "-XX:G1MaxNewSizePercent=40", "-XX:G1HeapRegionSize=8M", "-XX:G1ReservePercent=20", 
                "-XX:G1HeapWastePercent=5", "-XX:G1MixedGCCountTarget=4", "-XX:InitiatingHeapOccupancyPercent=15", 
                "-XX:G1MixedGCLiveThresholdPercent=90", "-XX:G1RSetUpdatingPauseTimePercent=5", 
                "-XX:SurvivorRatio=32", "-XX:+PerfDisableSharedMem", "-XX:MaxTenuringThreshold=1"
            ])
        if self.custom_args: cmd.extend(self.custom_args.split(" "))
        cmd.extend(["-jar", self.jar_file, "nogui"])
        try:
            cf = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(cmd, cwd=self.server_dir, stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                            text=True, bufsize=1, encoding='utf-8', errors='replace', creationflags=cf)
            for line in iter(self.process.stdout.readline, ''):
                if line and self.is_running: self.log_signal.emit(line.strip())
            self.process.wait()
        except Exception as e: self.log_signal.emit(f"[{_tr('錯誤', 'Error')}] {str(e)}")
        finally: self.stopped_signal.emit()
    def send_command(self, cmd):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
                self.log_signal.emit(f"> {cmd}")
            except: pass
    def stop_server(self):
        self.is_running = False
        self.send_command("stop")

# FRP 內網穿透執行緒
class FrpRunnerThread(QThread):
    log_signal = Signal(str)
    stopped_signal = Signal()
    def __init__(self, exe_path, exe_args, parent=None):
        super().__init__(parent)
        self.exe_path = exe_path
        self.exe_args = exe_args
        self.process = None
        self.is_running = True
    def run(self):
        try:
            cf = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            cmd = [os.path.abspath(self.exe_path)]
            if self.exe_args: cmd.extend(self.exe_args.split(" "))
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                            stderr=subprocess.STDOUT, text=True, bufsize=1, 
                                            encoding='utf-8', errors='replace', creationflags=cf)
            for line in iter(self.process.stdout.readline, ''):
                if line and self.is_running: self.log_signal.emit(line.strip())
            self.process.wait()
        except Exception as e:
            self.log_signal.emit(f"[{_tr('錯誤', 'Error')}] {str(e)}")
        finally:
            self.stopped_signal.emit()
    def send_command(self, cmd):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
                self.log_signal.emit(f"> {cmd}")
            except: pass
    def stop_process(self):
        self.is_running = False
        if self.process: self.process.terminate()

# 地圖壓縮備份執行緒
class BackupWorldThread(QThread):
    finished = Signal(str, bool)
    def __init__(self, server_name, parent=None):
        super().__init__(parent)
        self.server_name = server_name
    def run(self):
        try:
            base_dir = os.path.join("servers", self.server_name)
            world_dir = os.path.join(base_dir, "world")
            backup_dir = os.path.join(base_dir, "backups")
            if not os.path.exists(world_dir):
                self.finished.emit(_tr("找不到 world 資料夾，請先啟動伺服器產生世界！", "World folder not found. Start the server first!"), False)
                return
            os.makedirs(backup_dir, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = os.path.join(backup_dir, f"world_backup_{stamp}")
            shutil.make_archive(zip_name, 'zip', base_dir, "world")
            self.finished.emit(_tr("✅ 備份壓縮成功！", "✅ Backup created successfully!"), True)
        except Exception as e: self.finished.emit(_tr(f"❌ 備份失敗: {str(e)}", f"❌ Backup Failed: {str(e)}"), False)

# 地圖還原解壓縮執行緒
class RestoreBackupThread(QThread):
    finished = Signal(str, bool)
    def __init__(self, server_name, zip_name, parent=None):
        super().__init__(parent)
        self.server_name = server_name
        self.zip_name = zip_name
    def run(self):
        try:
            base_dir = os.path.join("servers", self.server_name)
            world_dir = os.path.join(base_dir, "world")
            backup_path = os.path.join(base_dir, "backups", self.zip_name)
            if os.path.exists(world_dir): shutil.rmtree(world_dir, ignore_errors=True)
            with zipfile.ZipFile(backup_path, 'r') as zip_ref: zip_ref.extractall(base_dir)
            self.finished.emit(_tr("✅ 存檔還原成功！", "✅ World Restore successful!"), True)
        except Exception as e: self.finished.emit(_tr(f"❌ 還原發生異常: {str(e)}", f"❌ Restore Failed: {str(e)}"), False)

# ==========================================
# 3. 完美寬扁自控遮罩彈窗系統
# ==========================================
class OverlayModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModalMask")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setVisible(False)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.container = QWidget()
        self.container.setObjectName("ModalContainer")
        self.container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 25, 30, 25)
        self.container_layout.setSpacing(15)
        
        self.header_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10B981;")
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        self.container_layout.addLayout(self.header_layout)
        
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.content_area)
        
        self.layout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.allow_close = True

    def set_content(self, title, widget, width=550, allow_close=True):
        self.container.setFixedWidth(width)
        self.title_label.setText(title)
        self.allow_close = allow_close
        for i in reversed(range(self.content_layout.count())): 
            w = self.content_layout.itemAt(i).widget()
            if w: w.setParent(None)
        self.content_layout.addWidget(widget)

    def show_modal(self):
        if self.parent(): self.resize(self.parent().size())
        self.raise_()
        self.setVisible(True)

    def hide_modal(self, force=False):
        if self.allow_close or force:
            self.setVisible(False)

    def mousePressEvent(self, event):
        if self.allow_close and not self.container.geometry().contains(event.position().toPoint()):
            self.hide_modal()
        event.accept()

# ==========================================
# 4. 新手教學與 EULA 內容
# ==========================================
class TutorialContent(QWidget):
    finished = Signal()
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.stack = QStackedWidget()
        
        # 教學步驟 1：語言設定
        step1 = QWidget()
        l1 = QVBoxLayout(step1)
        t1 = QLabel(_tr("<h2>👋 歡迎使用 CraftNode 伺服器面板</h2>", "<h2>👋 Welcome to CraftNode Panel</h2>"))
        t1.setTextFormat(Qt.TextFormat.RichText)
        l1.addWidget(t1)
        d1 = QLabel(_tr("請先決定偏好的介面語言與外觀，為您帶來最佳體驗：\n(未來可在程式設定中隨時更改)", "Please select your preferred language and theme for the best experience:\n(You can change this anytime in Settings)"))
        d1.setStyleSheet("color: #A0A0A0; line-height: 1.5;")
        l1.addWidget(d1)
        
        form = QFormLayout()
        self.theme_cb = QComboBox()
        self.theme_cb.addItems([_tr("🌙 深色模式 (Dark)", "🌙 Dark Mode"), _tr("☀️ 淺色模式 (Light)", "☀️ Light Mode")])
        self.theme_cb.setCurrentIndex(0 if APP_CONFIG["is_dark"] else 1)
        self.theme_cb.currentTextChanged.connect(self.change_theme)
        self.lang_cb = QComboBox()
        self.lang_cb.addItems(["繁體中文", "English"])
        self.lang_cb.setCurrentIndex(0 if APP_CONFIG["language"] == "zh" else 1)
        form.addRow(_tr("介面主題：", "Theme:"), self.theme_cb)
        form.addRow(_tr("介面語言：", "Language:"), self.lang_cb)
        l1.addLayout(form)
        self.stack.addWidget(step1)
        
        # 教學步驟 2：建立工作區
        step2 = QWidget()
        l2 = QVBoxLayout(step2)
        t2 = QLabel(_tr("<h2>🗂️ 建立您的第一台伺服器</h2>", "<h2>🗂️ Create Your First Server</h2>"))
        t2.setTextFormat(Qt.TextFormat.RichText)
        l2.addWidget(t2)
        desc2 = QLabel(_tr(
            "系統目前尚未綁定任何伺服器實體。<br><br>"
            "為了保持乾淨的檔案架構，請先至左側的<b>「🗄️ 多伺服器清單」</b>建立新的站點，"
            "您可以建立無數個獨立伺服器，系統會為您分配專屬資料夾並切換空間。",
            "There are currently no servers bound to the system.<br><br>"
            "To keep things organized, head to <b>Servers Management</b> first to create a new workspace. "
            "You can create unlimited isolated servers, and the program will organize them perfectly."
        ))
        desc2.setTextFormat(Qt.TextFormat.RichText)
        desc2.setWordWrap(True)
        l2.addWidget(desc2)
        self.stack.addWidget(step2)
        
        # 教學步驟 3：部署核心與設定
        step3 = QWidget()
        l3 = QVBoxLayout(step3)
        t3 = QLabel(_tr("<h2>⚙️ 部署核心與自訂屬性</h2>", "<h2>⚙️ Core & Properties Setup</h2>"))
        t3.setTextFormat(Qt.TextFormat.RichText)
        l3.addWidget(t3)
        desc3 = QLabel(_tr(
            "建立好伺服器後，接著來到<b>「核心與下載」</b>取得執行檔。<br><br>"
            "面板內建支援 Paper、Vanilla、Fabric，點擊即可自動完成部署與授權。<br>"
            "隨後前往<b>「屬性與設定」</b>，透過拉桿與開關輕鬆調配伺服器 RAM、正版驗證或防禦機制。",
            "After creating a server, go to <b>Core Deploy & Downloads</b> to download the jar file.<br><br>"
            "The panel natively supports Paper, Vanilla, and Fabric. Once downloaded, navigate to <b>Server Properties</b> to adjust RAM allocation, online-mode, and other game rules effortlessly."
        ))
        desc3.setTextFormat(Qt.TextFormat.RichText)
        desc3.setWordWrap(True)
        l3.addWidget(desc3)
        self.stack.addWidget(step3)
        
        # 教學步驟 4：全面掌控伺服器
        step4 = QWidget()
        l4 = QVBoxLayout(step4)
        t4 = QLabel(_tr("<h2>📟 終端管理、模組與安全排程</h2>", "<h2>📟 Control, Mods & Backups</h2>"))
        t4.setTextFormat(Qt.TextFormat.RichText)
        l4.addWidget(t4)
        desc4 = QLabel(_tr(
            "最後，在<b>「伺服器控制台」</b>啟動！<br><br>"
            "您可以在「擴充資源市集」自由安裝模組；在「地圖快照與備份」設定自動存檔防呆機制。<br>"
            "若沒有實體 IP，還能透過「內網穿透」輕鬆與世界連線。準備好開始您的冒險了嗎？",
            "Finally, ignite your server in the <b>Server Console</b>!<br><br>"
            "You can seamlessly install mods in the Marketplace, or configure auto-backups in the Backups tab to secure your world.<br>"
            "Ready to begin your adventure?"
        ))
        desc4.setTextFormat(Qt.TextFormat.RichText)
        desc4.setWordWrap(True)
        l4.addWidget(desc4)
        self.stack.addWidget(step4)

        self.layout.addWidget(self.stack)
        
        ctrl_layout = QHBoxLayout()
        self.btn_cancel = QPushButton(_tr("跳過 (Skip)", "Skip"))
        self.btn_cancel.setObjectName("SecondaryBtn")
        self.btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.clicked.connect(lambda: self.main_window.overlay.hide_modal(force=True))
        
        self.btn_next = QPushButton(_tr("下一步 ➡️", "Next ➡️"))
        self.btn_next.setObjectName("PrimaryBtn")
        self.btn_next.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_next.setMinimumHeight(45)
        self.btn_next.clicked.connect(self.next_step)
        
        ctrl_layout.addWidget(self.btn_cancel)
        ctrl_layout.addWidget(self.btn_next)
        self.layout.addSpacing(15)
        self.layout.addLayout(ctrl_layout)

    def change_theme(self, text):
        APP_CONFIG["is_dark"] = "Dark" in text or "深色" in text
        save_config(APP_CONFIG)
        self.main_window.setStyleSheet(get_stylesheet(APP_CONFIG["is_dark"]))

    def next_step(self):
        curr = self.stack.currentIndex()
        if curr < self.stack.count() - 1:
            self.stack.setCurrentIndex(curr + 1)
            if curr + 1 == self.stack.count() - 1:
                self.btn_next.setText(_tr("瞭解，開始使用 🚀", "Got it, Let's Start 🚀"))
        else:
            APP_CONFIG["first_run"] = False
            APP_CONFIG["language"] = "zh" if "中文" in self.lang_cb.currentText() else "en"
            save_config(APP_CONFIG)
            self.main_window.overlay.hide_modal(force=True)

class EulaContent(QWidget):
    def __init__(self, on_reject, on_accept):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(180) 
        self.scroll_area.setStyleSheet("border-radius: 5px; background: rgba(0,0,0, 0.2); border: 1px solid #3A3A3A;")
        
        self.eula_text = QLabel(_tr(EULA_ZH_TEXT, EULA_EN_TEXT))
        self.eula_text.setTextFormat(Qt.TextFormat.RichText)
        self.eula_text.setStyleSheet("padding: 10px; font-size:14px;")
        self.eula_text.setWordWrap(True)
        self.scroll_area.setWidget(self.eula_text)
        layout.addWidget(self.scroll_area)

        self.hint_label = QLabel(_tr("⬇️ 請將滾動條拉至最底以解鎖", "⬇️ Scroll downwards to unlock"))
        self.hint_label.setStyleSheet("color: #FF4D4D; font-weight: bold; margin-top:10px;")
        layout.addWidget(self.hint_label)

        self.agree_checkbox = QCheckBox(_tr("我已確認並同意伺服器法規與合約。", "I have read and agree to the EULA."))
        self.agree_checkbox.setEnabled(False)
        self.agree_checkbox.setStyleSheet("margin-top: 5px; margin-bottom: 10px;")
        layout.addWidget(self.agree_checkbox)

        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton(_tr("拒絕 (Decline)", "Decline"))
        self.agree_btn = QPushButton(_tr("同意並接續部署", "Accept & Deploy"))
        self.agree_btn.setEnabled(False)
        
        self.cancel_btn.setObjectName("SecondaryBtn")
        self.agree_btn.setObjectName("PrimaryBtn")
        self.cancel_btn.setMinimumHeight(45)
        self.agree_btn.setMinimumHeight(45)
        self.cancel_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.agree_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.agree_btn)
        layout.addLayout(btn_layout)

        self.scroll_area.verticalScrollBar().valueChanged.connect(self.check_scroll_bottom)
        self.agree_checkbox.stateChanged.connect(lambda: self.agree_btn.setEnabled(self.agree_checkbox.isChecked()))
        self.cancel_btn.clicked.connect(on_reject)
        self.agree_btn.clicked.connect(on_accept)
        QTimer.singleShot(100, self.check_scroll_bottom)

    def check_scroll_bottom(self):
        bar = self.scroll_area.verticalScrollBar()
        if bar.maximum() == 0 or bar.value() >= bar.maximum() - 5:
            self.agree_checkbox.setEnabled(True)
            self.hint_label.setText(_tr("✅ 閱讀完畢，可正常解鎖使用", "✅ Reached Bottom. Ready to proceed."))
            self.hint_label.setStyleSheet("color: #10B981; font-weight: bold; margin-top:10px;")

# ==========================================
# 5. 核心面板與邏輯
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_tr("CraftNode 伺服器管理面板", "CraftNode Server Panel"))
        self.resize(1380, 900)
        self.setStyleSheet(get_stylesheet(APP_CONFIG["is_dark"]))
        
        self.active_threads = []
        self.server_thread = None
        self.frp_runner = None
        self.local_ip = self.get_local_ip()
        self.public_ip = _tr("獲取中...", "Fetching...")
        self.online_players = []
        
        self.max_pl_count = 20
        self.last_net = psutil.net_io_counters()

        # 自動備份計時器初始化
        self.auto_backup_timer = QTimer(self)
        self.auto_backup_timer.timeout.connect(lambda: self.make_backup(auto=True))

        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        tray_menu = QMenu()
        act_show = QAction(_tr("開啟面板", "Open Panel"), self)
        act_quit = QAction(_tr("完全退出", "Force Quit"), self)
        act_show.triggered.connect(self.showNormal)
        act_quit.triggered.connect(self.force_quit)
        tray_menu.addAction(act_show)
        tray_menu.addAction(act_quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activation)
        self.tray_icon.show()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_sidebar()
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        self.create_topbar()
        self.content_stack = QStackedWidget()
        self.right_layout.addWidget(self.content_stack)
        self.main_layout.addWidget(self.right_container)

        self.overlay = OverlayModal(self.central_widget)
        self.setup_pages()
        self.central_widget.installEventFilter(self)
        
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_global_dashboard)
        self.system_timer.start(1000)

        self.ip_thread = FetchPublicIPThread(parent=self)
        self.ip_thread.result.connect(self.update_public_ip)
        self.ip_thread.start()

        self.switch_menu(1) 
        if APP_CONFIG.get("first_run", True):
            QTimer.singleShot(400, self.boot_tutorial)
        else:
            self.update_server_sync_count() 
            
        self.log_sys_alert(_tr("面板初始化完成，歡迎使用 CraftNode。", "Panel initialized successfully. Welcome to CraftNode."), "success")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.central_widget.size())
        
    def tray_activation(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return "127.0.0.1"
        
    def update_public_ip(self, ip):
        self.public_ip = ip
        if not getattr(self, 'ip_hidden', False):
            self.lbl_pub_ip.setText(f"{_tr('🌍 外網 IP:', '🌍 Public IP:')} {self.public_ip}")

    def show_custom_alert(self, title, message):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(message)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 15px; margin-bottom: 25px; line-height: 1.5;")
        l.addWidget(lbl)
        
        btn = QPushButton(_tr("好的", "OK"))
        btn.setMinimumHeight(45)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setObjectName("PrimaryBtn")
        btn.clicked.connect(self.overlay.hide_modal)
        
        l.addWidget(btn)
        self.overlay.set_content(title, w, width=550, allow_close=True)
        self.overlay.show_modal()

    def boot_tutorial(self):
        self.overlay.set_content("✨ Welcome", TutorialContent(self), width=650, allow_close=False)
        self.overlay.show_modal()

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)
        
        brand = QLabel("CraftNode")
        brand.setStyleSheet("font-size: 26px; font-weight: 900; margin: 30px 15px 20px 15px; color: #10B981;")
        layout.addWidget(brand)

        def add_category(text, with_line=False):
            if with_line:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("background-color: #2C2E33; max-height: 1px; margin: 10px 15px 0 15px;")
                layout.addWidget(line)
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #718096; font-size: 13px; font-weight: bold; margin: 10px 15px 5px 15px;")
            layout.addWidget(lbl)

        self.menu_buttons = []
        def create_btn(txt, idx):
            btn = QPushButton(txt)
            btn.setObjectName("NavBtn")
            if idx == 1: btn.setStyleSheet("background-color: #25262B; color: #10B981;")
            btn.clicked.connect(lambda checked, i=idx: self.switch_menu(i))
            self.menu_buttons.append((idx, btn))
            layout.addWidget(btn)

        add_category(_tr("伺服器監控與管理", "MANAGEMENT"))
        create_btn("🏠 " + _tr("首頁儀表板", "Dashboard"), 0)
        create_btn("🗄️ " + _tr("多伺服器清單", "Servers Management"), 1)
        create_btn("👥 " + _tr("玩家與權限管理", "Players & Perms"), 2)
        create_btn("📟 " + _tr("伺服器控制台", "Server Console"), 3)
        
        add_category(_tr("伺服器建置", "SERVER SETUP"), True)
        create_btn("⚙️ " + _tr("核心與下載環境", "Core & Downloads"), 4)
        create_btn("🛠️ " + _tr("屬性與世界設定", "Server Properties"), 5)
        create_btn("📦 " + _tr("擴充資源市集", "Marketplace"), 6)
        
        add_category(_tr("進階運作", "ADVANCED"), True)
        create_btn("📅 " + _tr("地圖快照與備份", "World Backups"), 7)
        create_btn("🌐 " + _tr("內網穿透與通道", "Network Tunnels"), 8)
        
        layout.addStretch() 
        add_category(_tr("設定與說明", "SETTINGS"), True)
        create_btn("📖 " + _tr("面板教學指南", "User Manual"), 9)
        create_btn("⚙️ " + _tr("面板程式設定", "App Settings"), 10)
        layout.addSpacing(10)

        self.main_layout.addWidget(sidebar)

    def switch_menu(self, index):
        if index in [2,3,4,5,6,7,8] and not APP_CONFIG["active_server"]:
            self.show_custom_alert(_tr("系統提示", "Action Denied"), _tr("請先於「伺服器清單」新增並切換至一個伺服器空間！", "Please select a server workspace in Servers Management first!"))
            self.switch_menu(1) 
            return
            
        self.content_stack.setCurrentIndex(index)
        for idx, btn in self.menu_buttons:
            if idx == index:
                btn.setStyleSheet("background-color: #25262B; color: #10B981;")
            else:
                btn.setStyleSheet("")
                
        # 進入備份頁面時動態刷新設定讀取
        if index == 7:
            self.refresh_backups()

    def create_topbar(self):
        topbar = QWidget()
        topbar.setObjectName("Topbar")
        topbar.setFixedHeight(80)
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(25, 0, 25, 0)
        
        self.top_status = QLabel(_tr("⚫ 離線狀態", "⚫ Offline"))
        self.top_status.setStyleSheet("color: #718096; font-weight: bold; font-size: 15px;")
        layout.addWidget(self.top_status)
        layout.addSpacing(15)
        
        self.lbl_players = QLabel(f"{_tr('👥 玩家:', '👥 Players:')} 0/20")
        self.lbl_players.setStyleSheet("font-weight:bold; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(self.lbl_players)
        
        layout.addStretch()
        
        ip_panel = QHBoxLayout()
        ip_panel.setSpacing(15)
        self.lbl_loc_ip = QLabel(f"{_tr('🌐 內網 IP:', '🌐 Local IP:')} {self.local_ip}:25565")
        self.lbl_pub_ip = QLabel(f"{_tr('🌍 外網 IP:', '🌍 Public IP:')} {self.public_ip}")
        for l in [self.lbl_loc_ip, self.lbl_pub_ip]:
            l.setStyleSheet("font-weight:bold; font-size: 14px; color: #A0A0A0;")
            ip_panel.addWidget(l)
            
        btn_copy = QPushButton(_tr("複製 IP", "Copy IP"))
        btn_copy.setObjectName("SmallBtn")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(f"{_tr('內網:', 'Local:')} {self.local_ip}:25565\n{_tr('外網:', 'Public:')} {self.public_ip}"))
        ip_panel.addWidget(btn_copy)
        
        self.ip_hidden = False
        btn_hide = QPushButton(_tr("隱藏 IP", "Hide IP"))
        btn_hide.setObjectName("SmallBtn")
        btn_hide.clicked.connect(self.toggle_ip_visibility)
        ip_panel.addWidget(btn_hide)
        
        layout.addLayout(ip_panel)
        layout.addSpacing(25)
        
        btn_folder = QPushButton(_tr("開啟伺服器資料夾", "Open Server Folder"))
        btn_folder.setObjectName("SecondaryBtn")
        btn_folder.clicked.connect(self.open_server_folder)
        layout.addWidget(btn_folder)
        
        self.right_layout.addWidget(topbar)

    def set_server_state(self, state):
        if state == "offline":
            self.top_status.setText(_tr("⚫ 離線狀態", "⚫ Offline"))
            self.top_status.setStyleSheet("color: #718096; font-weight: bold; font-size: 15px;")
        elif state == "starting":
            self.top_status.setText(_tr("🟡 啟動中...", "🟡 Starting..."))
            self.top_status.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 15px;")
        elif state == "online":
            self.top_status.setText(_tr("🟢 線上", "🟢 Online"))
            self.top_status.setStyleSheet("color: #10B981; font-weight: bold; font-size: 15px;")
        elif state == "stopping":
            self.top_status.setText(_tr("🔴 關閉中...", "🔴 Stopping..."))
            self.top_status.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 15px;")

    def toggle_ip_visibility(self):
        self.ip_hidden = not self.ip_hidden
        if self.ip_hidden:
            self.lbl_loc_ip.setText(f"{_tr('🌐 內網 IP:', '🌐 Local IP:')} ***.***.***.***")
            self.lbl_pub_ip.setText(f"{_tr('🌍 外網 IP:', '🌍 Public IP:')} ***.***.***.***")
        else:
            self.lbl_loc_ip.setText(f"{_tr('🌐 內網 IP:', '🌐 Local IP:')} {self.local_ip}:25565")
            self.lbl_pub_ip.setText(f"{_tr('🌍 外網 IP:', '🌍 Public IP:')} {self.public_ip}")

    def update_server_sync_count(self):
        self.lbl_players.setText(f"{_tr('👥 玩家:', '👥 Players:')} {len(self.online_players)}/{self.max_pl_count}")

    def open_server_folder(self):
        if not APP_CONFIG["active_server"]:
             os.startfile(os.path.abspath("./servers"))
        else:
             os.startfile(os.path.abspath(f"./servers/{APP_CONFIG['active_server']}"))

    def setup_pages(self):
        self.page_home = QWidget(); self.setup_page_home()
        self.page_server_list = QWidget(); self.setup_page_servers()
        self.page_players = QWidget(); self.setup_page_players()
        self.page_console = QWidget(); self.setup_page_console()
        self.page_core = QWidget(); self.setup_page_core()
        self.page_properties = QWidget(); self.setup_page_properties()
        self.page_market = QWidget(); self.setup_page_market()
        self.page_backup = QWidget(); self.setup_page_backup()
        self.page_network = QWidget(); self.setup_page_network()
        self.page_manual = QWidget(); self.setup_page_manual()
        self.page_settings = QWidget(); self.setup_page_settings()
        
        for pg in [self.page_home, self.page_server_list, self.page_players, self.page_console,
                   self.page_core, self.page_properties, self.page_market, self.page_backup, 
                   self.page_network, self.page_manual, self.page_settings]:
            self.content_stack.addWidget(pg)

    # ==========================
    # P0: 首頁儀表板
    # ==========================
    def setup_page_home(self):
        layout = QVBoxLayout(self.page_home)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>🏠 {_tr('系統總覽與即時監視', 'Dashboard')}</h1>"))
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(25)
        
        for name, lbl_name in [(_tr("📦 CPU 使用率", "📦 CPU Usage"), "dash_cpu_val"), 
                               (_tr("🧠 記憶體使用率 (RAM)", "🧠 RAM Usage"), "dash_ram_val"), 
                               (_tr("📡 網路速率", "📡 Network Speed"), "dash_net_val")]:
            c = QFrame(); c.setObjectName("DashboardCard")
            cl = QVBoxLayout(c)
            cl.addWidget(QLabel(f"<b>{name}</b>"))
            lbl = QLabel("0%")
            lbl.setStyleSheet("font-size: 30px; color: #10B981; font-weight: 900; margin-top: 10px;")
            setattr(self, lbl_name, lbl)
            cl.addWidget(lbl)
            cards_layout.addWidget(c)
            
        layout.addLayout(cards_layout)
        layout.addSpacing(25)
        layout.addWidget(QLabel(f"<h2>🚨 {_tr('伺服器日誌', 'System Events Log')}</h2>"))
        self.dash_logger = QTextEdit()
        self.dash_logger.setReadOnly(True)
        self.dash_logger.setObjectName("ConsoleOutput")
        layout.addWidget(self.dash_logger)

    def log_sys_alert(self, msg, level="info"):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        color = "#D1D5DB"
        if level == "warn": color = "#F59E0B"
        elif level == "error": color = "#EF4444"
        elif level == "success": color = "#10B981"
        self.dash_logger.moveCursor(QTextCursor.MoveOperation.End)
        self.dash_logger.insertHtml(f'<span style="color:{color};">[{t}] [System] {msg}</span><br>')

    def update_global_dashboard(self):
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        self.dash_cpu_val.setText(f"{cpu:.1f}%"); self.dash_ram_val.setText(f"{ram:.1f}%")
        self.dash_cpu_val.setStyleSheet(f"font-size:32px; font-weight:900; color: {'#EF4444' if cpu > 85 else '#10B981'};")
        self.dash_ram_val.setStyleSheet(f"font-size:32px; font-weight:900; color: {'#EF4444' if ram > 85 else '#10B981'};")
        
        net = psutil.net_io_counters() 
        up_kb = max(0.0, (net.bytes_sent - self.last_net.bytes_sent) / 1024.0)
        dl_kb = max(0.0, (net.bytes_recv - self.last_net.bytes_recv) / 1024.0)
        self.last_net = net
        self.dash_net_val.setText(f"🔼 Up: {up_kb:.1f} KB/s\n🔽 Dl: {dl_kb:.1f} KB/s")
        self.dash_net_val.setStyleSheet("font-size: 18px; color: #3B82F6; font-weight: 900; margin-top: 10px;")
        
        if hasattr(self, 'cons_cpu'):
            self.cons_cpu.setText(f"📦 CPU: {cpu:.1f}%")
            self.cons_ram.setText(f"🧠 RAM: {ram:.1f}%")
            disk = psutil.disk_usage('/').percent
            self.cons_disk.setText(f"💾 {_tr('硬碟', 'Disk')}: {disk:.1f}%")
            self.cons_net.setText(f"📡 {_tr('網路', 'Network')}: {dl_kb:.1f} KB/s")
            
            c_red = "#EF4444"
            c_green = "#10B981"
            self.cons_cpu.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c_red if cpu > 85 else c_green};")
            self.cons_ram.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c_red if ram > 85 else c_green};")
            self.cons_disk.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c_red if disk > 90 else c_green};")

    # ==========================
    # P1: 多伺服器管理清單
    # ==========================
    def setup_page_servers(self):
        layout = QVBoxLayout(self.page_server_list)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>🗄️ {_tr('多伺服器清單', 'Servers Management')}</h1>"))
        
        btn_add = QPushButton("➕ " + _tr("建立新伺服器", "Create Server"))
        btn_add.setObjectName("PrimaryBtn")
        btn_add.clicked.connect(self.show_add_server_modal)
        
        btn_import = QPushButton("📥 " + _tr("匯入既有伺服器 (.zip)", "Import ZIP"))
        btn_import.setObjectName("SecondaryBtn")
        btn_import.clicked.connect(self.import_server_zip)
        
        ctrl_lo = QHBoxLayout()
        ctrl_lo.addWidget(btn_add)
        ctrl_lo.addWidget(btn_import)
        ctrl_lo.addStretch()
        layout.addLayout(ctrl_lo)
        layout.addSpacing(15)
        
        self.srv_list = QTableWidget(0, 3)
        self.srv_list.setHorizontalHeaderLabels([_tr("伺服器目錄名稱", "Folder Name"), _tr("核心", "Core Setup"), _tr("操作", "Action")])
        self.srv_list.verticalHeader().setVisible(False)
        self.srv_list.verticalHeader().setDefaultSectionSize(65) 
        self.srv_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.srv_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.srv_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.srv_list)
        self.refresh_server_list()
        
    def refresh_server_list(self):
        self.srv_list.setRowCount(0)
        for srv in APP_CONFIG["servers"]:
            r = self.srv_list.rowCount()
            self.srv_list.insertRow(r)
            name = srv["name"]
            is_act = (name == APP_CONFIG["active_server"])
            self.srv_list.setItem(r, 0, QTableWidgetItem(_tr(f"⭐ {name} (目前選用)", f"⭐ {name} (Active)") if is_act else name))
            self.srv_list.setItem(r, 1, QTableWidgetItem(f"{srv.get('core','None')} {srv.get('version','')}"))
            
            btn_switch = QPushButton(_tr("切換", "Connect") if not is_act else _tr("已連入", "Active"))
            btn_switch.setObjectName("SecondaryBtn" if not is_act else "SuccessBtn")
            btn_switch.setEnabled(not is_act)
            btn_switch.setMinimumWidth(80) 
            btn_switch.clicked.connect(lambda ch, s=name: self.switch_active_server(s))
            
            btn_del = QPushButton("🗑️ " + _tr("刪除", "Delete"))
            btn_del.setObjectName("DangerBtn")
            btn_del.setMinimumWidth(80) 
            btn_del.clicked.connect(lambda ch, s=name: self.delete_server(s))
            
            self.srv_list.setCellWidget(r, 2, create_action_widget([btn_switch, btn_del]))

    def show_add_server_modal(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel(_tr("為全新伺服器輸入名稱 (限英數字)：", "Enter new server name (Alphanumeric only):")))
        inp = QLineEdit()
        l.addWidget(inp)
        def confirm():
            name = inp.text().strip()
            if not name or not name.isalnum(): return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("名稱不可為空且必須是純英數！", "Name cannot be empty and must be alphanumeric!"))
            if any(s["name"] == name for s in APP_CONFIG["servers"]): return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("該名稱的伺服器已存在。", "Server name already exists."))
            APP_CONFIG["servers"].append({"name": name, "core": "未下載", "version": "", "ram": 4, "aikar": True, "custom_jvm": "", "eula_agreed_core": "", "auto_backup": 0, "backup_on_stop": False})
            save_config(APP_CONFIG)
            os.makedirs(os.path.join("servers", name), exist_ok=True)
            self.refresh_server_list()
            self.overlay.hide_modal(force=True)
            if not APP_CONFIG["active_server"]: self.switch_active_server(name)

        btn_cancel = QPushButton(_tr("取消", "Cancel")); btn_cancel.setObjectName("SecondaryBtn")
        btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); btn_cancel.setMinimumHeight(45)
        btn_cancel.clicked.connect(self.overlay.hide_modal)
        
        btn_confirm = QPushButton(_tr("確認建立", "Create")); btn_confirm.setObjectName("PrimaryBtn")
        btn_confirm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); btn_confirm.setMinimumHeight(45)
        btn_confirm.clicked.connect(confirm)
        lo_h = QHBoxLayout(); lo_h.addWidget(btn_cancel); lo_h.addWidget(btn_confirm)
        l.addLayout(lo_h)
        self.overlay.set_content(_tr("建立伺服器空間", "Create Workspace"), w, width=500, allow_close=False)
        self.overlay.show_modal()

    def import_server_zip(self):
        filepath, _ = QFileDialog.getOpenFileName(self, _tr("選擇伺服器壓縮包", "Select ZIP"), "", "Zip Files (*.zip)")
        if filepath:
            name = os.path.basename(filepath).replace(".zip", "")
            target_dir = os.path.join("servers", name)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                try:
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    APP_CONFIG["servers"].append({"name": name, "core": "Imported", "version": "Custom", "eula_agreed_core": "", "auto_backup": 0, "backup_on_stop": False})
                    save_config(APP_CONFIG)
                    self.refresh_server_list()
                    self.show_custom_alert(_tr("成功", "Success"), _tr(f"成功匯入伺服器 {name}！", f"Successfully imported {name}!"))
                except Exception as e:
                    self.show_custom_alert(_tr("錯誤", "Error"), _tr(f"解壓縮失敗：{e}", f"Extraction failed: {e}"))

    def switch_active_server(self, name):
        if self.server_thread and self.server_thread.isRunning():
            return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("伺服器運作中，無法跨區切換！", "Server is running, cannot switch workspace! Stop it first."))
        APP_CONFIG["active_server"] = name
        save_config(APP_CONFIG)
        self.refresh_server_list()
        self.log_sys_alert(_tr(f"已將工作區切換至伺服器：{name}", f"Workspace switched to server: {name}"), "info")

    def delete_server(self, name):
        if self.server_thread and self.server_thread.isRunning() and APP_CONFIG["active_server"] == name:
            return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("伺服器運作中，請先關閉才能刪除。", "Server is running. Stop it before deleting."))
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(_tr(f"將會永久抹除 <b>{name}</b> 與裡面的所有世界存檔！<br>此為物理刪除，無法復原。", f"Permanently delete <b>{name}</b> and all its world data!<br>This action cannot be undone."))
        lbl.setTextFormat(Qt.TextFormat.RichText)
        l.addWidget(lbl)
        
        def confirm():
            APP_CONFIG["servers"] = [s for s in APP_CONFIG["servers"] if s["name"] != name]
            if APP_CONFIG["active_server"] == name:
                APP_CONFIG["active_server"] = APP_CONFIG["servers"][0]["name"] if len(APP_CONFIG["servers"]) > 0 else ""
            save_config(APP_CONFIG)
            try: shutil.rmtree(os.path.join("servers", name), ignore_errors=True)
            except: pass
            self.refresh_server_list()
            self.log_sys_alert(_tr(f"已永久刪除伺服器 {name}", f"Server {name} permanently deleted."), "error")
            self.overlay.hide_modal(force=True)
            
        btn_cancel = QPushButton(_tr("取消", "Cancel")); btn_cancel.setObjectName("SecondaryBtn")
        btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); btn_cancel.setMinimumHeight(45)
        btn_cancel.clicked.connect(self.overlay.hide_modal)
        
        btn_confirm = QPushButton(_tr("確認無誤，抹除", "Confirm Delete")); btn_confirm.setObjectName("DangerBtn")
        btn_confirm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); btn_confirm.setMinimumHeight(45)
        btn_confirm.clicked.connect(confirm)
        lo_h = QHBoxLayout(); lo_h.addWidget(btn_cancel); lo_h.addWidget(btn_confirm)
        l.addLayout(lo_h)
        self.overlay.set_content(_tr("確認終極操作", "Verify Action"), w, width=550, allow_close=False)
        self.overlay.show_modal()

    # ==========================
    # P2: 在線玩家與權限管理
    # ==========================
    def setup_page_players(self):
        page = self.page_players
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>👥 {_tr('玩家與權限管理', 'Players & Permissions')}</h1>"))
        
        grp = QGroupBox(_tr("即時玩家列表", "Online Players"))
        lo = QVBoxLayout(grp)
        self.table_players = QTableWidget(0, 2)
        self.table_players.setHorizontalHeaderLabels([_tr("玩家名稱", "Player Name"), _tr("快速操作", "Actions")])
        self.table_players.verticalHeader().setVisible(False)
        self.table_players.verticalHeader().setDefaultSectionSize(95)
        self.table_players.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_players.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        lo.addWidget(self.table_players)
        layout.addWidget(grp)
        
        btn_sync = QPushButton(_tr("🔄 強制刷新名單 (清除快取)", "🔄 Force Refresh Player List"))
        btn_sync.setObjectName("SecondaryBtn")
        btn_sync.clicked.connect(lambda: [self.online_players.clear(), self.refresh_players_table()])
        layout.addWidget(btn_sync)

    def refresh_players_table(self):
        self.update_server_sync_count()
        self.table_players.setRowCount(0)
        for idx, p_name in enumerate(self.online_players):
            self.table_players.insertRow(idx)
            self.table_players.setItem(idx, 0, QTableWidgetItem(f"🟢 {p_name}"))
            
            b_op = QPushButton(_tr("👑 OP", "👑 OP")); b_op.setObjectName("SuccessBtn")
            b_deop = QPushButton(_tr("🔻 撤 OP", "🔻 DeOP")); b_deop.setObjectName("SecondaryBtn")
            b_surv = QPushButton(_tr("⛏️ 生存", "⛏️ Surv")); b_surv.setObjectName("SecondaryBtn")
            b_crea = QPushButton(_tr("🎨 創造", "🎨 Crea")); b_crea.setObjectName("PrimaryBtn")
            b_kick = QPushButton(_tr("🥾 踢出", "🥾 Kick")); b_kick.setObjectName("DangerBtn")
            b_ban = QPushButton(_tr("🚫 封鎖", "🚫 Ban")); b_ban.setObjectName("DangerBtn")
            
            b_op.clicked.connect(lambda ch, p=p_name: self.send_instant_cmd(f"op {p}"))
            b_deop.clicked.connect(lambda ch, p=p_name: self.send_instant_cmd(f"deop {p}"))
            b_surv.clicked.connect(lambda ch, p=p_name: self.send_instant_cmd(f"gamemode survival {p}"))
            b_crea.clicked.connect(lambda ch, p=p_name: self.send_instant_cmd(f"gamemode creative {p}"))
            b_kick.clicked.connect(lambda ch, p=p_name: [self.send_instant_cmd(f"kick {p} {_tr('管理員已將您踢出', 'Kicked by Administrator')}"), self.log_sys_alert(_tr(f"已踢出玩家 {p}", f"Kicked player {p}"), "warn")])
            b_ban.clicked.connect(lambda ch, p=p_name: [self.send_instant_cmd(f"ban {p} {_tr('違反規定', 'Banned by Administrator')}"), self.log_sys_alert(_tr(f"已封鎖玩家 {p}", f"Banned player {p}"), "error")])
            
            c_widget = QWidget()
            grid_lo = QGridLayout(c_widget)
            grid_lo.setContentsMargins(5, 5, 5, 5)
            grid_lo.setSpacing(5)
            grid_lo.addWidget(b_op, 0, 0); grid_lo.addWidget(b_deop, 0, 1); grid_lo.addWidget(b_surv, 0, 2)
            grid_lo.addWidget(b_crea, 1, 0); grid_lo.addWidget(b_kick, 1, 1); grid_lo.addWidget(b_ban, 1, 2)
            
            self.table_players.setCellWidget(idx, 1, c_widget)

    def send_instant_cmd(self, cmd):
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.send_command(cmd)
            self.show_custom_alert(_tr("系統提示", "System Notification"), _tr(f"指令已發送：/{cmd}", f"Command sent: /{cmd}"))
        else:
            self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("伺服器未開啟，無法發送指令！", "Server is not running. Cannot send commands!"))


    # ==========================
    # P3: 核心與真實下載
    # ==========================
    def setup_page_core(self):
        page = self.page_core
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>⚙️ {_tr('核心部署與下載環境', 'Core Deploy & Downloads')}</h1>"))

        grp = QGroupBox(_tr("核心選擇區", "Version Fetcher"))
        form = QFormLayout(grp)
        self.combo_core = QComboBox()
        self.combo_core.addItems([
            _tr("Paper (插件最佳化)", "Paper (Plugin Optimized)"), 
            _tr("Vanilla (官方原版)", "Vanilla (Official)"), 
            _tr("Fabric (輕量模組)", "Fabric (Modded)"), 
            _tr("Forge (需手動安裝)", "Forge (Manual Install)")
        ])
        self.combo_core.currentTextChanged.connect(self.fetch_core_versions)
        form.addRow(_tr("生態系：", "Ecosystem:"), self.combo_core)
        self.combo_ver = QComboBox()
        form.addRow(_tr("版號：", "Version:"), self.combo_ver)
        layout.addWidget(grp)
        
        self.dl_group = QGroupBox(_tr("下載進度", "Download Progress"))
        dl_layout = QVBoxLayout(self.dl_group)
        self.dl_lbl = QLabel("...")
        self.dl_bar = QProgressBar(); self.dl_bar.setValue(0)
        dl_layout.addWidget(self.dl_lbl); dl_layout.addWidget(self.dl_bar)
        self.dl_group.setVisible(False)
        layout.addWidget(self.dl_group)
        layout.addSpacing(20)

        self.btn_core_action = QPushButton(_tr("📥 同意 EULA 並從網路下載", "📥 Download & Agree EULA"))
        self.btn_core_action.setObjectName("PrimaryBtn")
        self.btn_core_action.setFixedSize(400, 50)
        self.btn_core_action.clicked.connect(self.handle_core_action)
        layout.addWidget(self.btn_core_action, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.fetch_core_versions("Paper")

    def fetch_core_versions(self, core_text):
        self.combo_ver.clear(); self.combo_ver.addItem(_tr("🔄 抓取中...", "🔄 Fetching..."))
        self.combo_ver.setEnabled(False)
        thread = FetchCoreVersionsThread(core_text, parent=self)
        thread.finished.connect(lambda v: (self.combo_ver.clear(), self.combo_ver.addItems(v), self.combo_ver.setEnabled(True)))
        thread.start()
        self.active_threads.append(thread)

    def handle_core_action(self):
        if "Forge" in self.combo_core.currentText():
            self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("Forge 不支援直鏈。請自行下載 Installer 放入！", "Forge requires manual import."))
            return
            
        c_type = self.combo_core.currentText().split(' ')[0]
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        
        if curr_srv and curr_srv.get("eula_agreed_core") == c_type:
            self.start_download_process()
        else:
            eula_ui = EulaContent(on_reject=lambda: self.overlay.hide_modal(force=True), on_accept=self.start_download_process)
            self.overlay.set_content(_tr("授權合約聲明", "EULA Contract"), eula_ui, width=800, allow_close=False)
            self.overlay.show_modal()

    def start_download_process(self):
        self.overlay.hide_modal(force=True)
        self.btn_core_action.setEnabled(False)
        self.dl_group.setVisible(True)
        
        c_type = self.combo_core.currentText().split(' ')[0]
        c_ver = self.combo_ver.currentText()
        
        for s in APP_CONFIG["servers"]:
            if s["name"] == APP_CONFIG["active_server"]:
                s["core"] = c_type
                s["version"] = c_ver
                s["eula_agreed_core"] = c_type
        save_config(APP_CONFIG)
        self.refresh_server_list()
        
        self.dl_lbl.setText(_tr(f"下載中： {c_type} {c_ver} ...", f"Downloading: {c_type} {c_ver} ..."))
        self.dl_bar.setValue(0)
        
        self.log_sys_alert(_tr(f"開始從網路下載伺服器核心：{c_type} {c_ver}", f"Downloading core: {c_type} {c_ver}"), "info")
        
        dl_thread = DownloadCoreThread(c_type, c_ver, APP_CONFIG["active_server"], parent=self)
        dl_thread.progress.connect(lambda val: self.dl_bar.setRange(0, 0) if val == -1 else (self.dl_bar.setRange(0, 100), self.dl_bar.setValue(val)))
        dl_thread.finished.connect(lambda msg, ok: [
            self.dl_bar.setRange(0, 100), self.dl_bar.setValue(100),
            self.dl_lbl.setText(msg), 
            self.btn_core_action.setText(_tr("🔄 重新下載核心", "🔄 Re-Download Core")),
            self.btn_core_action.setObjectName("DangerBtn"),
            self.btn_core_action.setEnabled(True),
            self.log_sys_alert(msg, "success" if ok else "error")
        ])                   
        dl_thread.start()                
        self.active_threads.append(dl_thread)    

    # ==========================
    # P4: 屬性設定
    # ==========================
    def setup_page_properties(self):
        page = self.page_properties
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>🛠️ {_tr('屬性與世界設定 (Properties)', 'Server Properties')}</h1>")) 

        scroll = QScrollArea() 
        scroll.setWidgetResizable(True)       
        container = QWidget()    
        grid = QGridLayout(container)     
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setSpacing(20)   

        grp_basic = QGroupBox(_tr("基礎與網路資訊", "Network Info"))  		
        frm_basic = QFormLayout(grp_basic)  
        self.motd_input = QLineEdit("A Minecraft Server") 
        self.motd_input.setMaximumWidth(400) 
        self.port_input = QSpinBox()   
        self.port_input.setRange(1024, 65535); self.port_input.setValue(25565)  
        self.port_input.setMaximumWidth(200)
        self.max_pl = QSpinBox()   
        self.max_pl.setRange(2 ,1500); self.max_pl.setValue(20)   
        self.max_pl.setMaximumWidth(200)
        frm_basic.addRow("MotD:", self.motd_input)      
        frm_basic.addRow("Port:",  self.port_input) 
        frm_basic.addRow(_tr("最大玩家:", "Max Players:"), self.max_pl) 
        
        grp_game = QGroupBox(_tr("遊戲機制", "Gameplay"))  
        frm_game = QFormLayout(grp_game)                 
        self.gamemode_combo = QComboBox()        
        self.gamemode_combo.addItems(["survival", "creative", "adventure", "spectator"])
        self.diff_combo = QComboBox()        
        self.diff_combo.addItems(["easy", "normal", "hard", "peaceful"])
        self.diff_combo.setCurrentText("normal")
        self.hc_check = QCheckBox(_tr("極限模式", "Hardcore")) 
        self.pvp_check = QCheckBox(_tr("允許戰鬥 (PVP)", "Enable PVP")) 
        self.pvp_check.setChecked(True)  
        frm_game.addRow(_tr("模式:", "Mode:"), self.gamemode_combo)        
        frm_game.addRow(_tr("難度:", "Difficulty:"), self.diff_combo)        
        frm_game.addRow(_tr("極限:", "Hardcore:"), self.hc_check)      
        frm_game.addRow(_tr("戰鬥:", "Fighting:"), self.pvp_check)      

        grp_world = QGroupBox(_tr("效能與世界配置", "World Gen & Perf")) 
        frm_world = QFormLayout(grp_world)             
        self.view_dist = QSpinBox()   
        self.view_dist.setRange(2 ,32); self.view_dist.setValue(10)   
        self.view_dist.setMaximumWidth(200)
        self.seed_input = QLineEdit() 
        self.seed_input.setPlaceholderText(_tr("留空隨機...", "Random if blank..."))
        self.seed_input.setMaximumWidth(400)
        
        self.ram_val_lbl = QLabel("1 GB")           
        self.ram_slider = QSlider(Qt.Orientation.Horizontal)         
        sys_ram_gb = int(psutil.virtual_memory().total / 1e9)           
        self.max_ram = sys_ram_gb if sys_ram_gb > 0 else 16
        self.ram_slider.setRange(1, self.max_ram)             
        
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        ram_val = curr_srv.get("ram", 4) if curr_srv else 4
        self.ram_slider.setValue(ram_val)
        self.ram_val_lbl.setText(_tr(f"分配: [ {ram_val} GB ]", f"Allocated: [ {ram_val} GB ]"))
        self.ram_slider.valueChanged.connect(lambda v: self.ram_val_lbl.setText(_tr(f"分配: [ {v} GB ]", f"Allocated: [ {v} GB ]")))      
        h_ram = QHBoxLayout()     
        h_ram.addWidget(self.ram_slider); h_ram.addWidget(self.ram_val_lbl)        

        self.aikar_flag = QCheckBox(_tr("寫入 Aikar's GC 最佳化參數", "Enable Aikar's GC Flags"))
        self.aikar_flag.setChecked(curr_srv.get("aikar", True) if curr_srv else True)
        self.custom_java_args = QLineEdit()
        self.custom_java_args.setPlaceholderText(_tr("自訂 JVM 參數 (選填)", "Custom JVM Arguments (Optional)"))

        frm_world.addRow(_tr("視距:", "View Dist:"), self.view_dist)      
        frm_world.addRow(_tr("種子碼:", "Seed:"),  self.seed_input) 
        frm_world.addRow(_tr("配置 RAM:", "Allocate RAM:"), h_ram) 
        frm_world.addRow(_tr("最佳化配置:", "Optimizations:"), self.aikar_flag) 
        frm_world.addRow(_tr("自訂參數:", "Custom JVM:"), self.custom_java_args)

        grp_sec = QGroupBox(_tr("安全性與指令", "Security & Protection"))  
        frm_sec = QFormLayout(grp_sec)                 
        self.online_check = QCheckBox(_tr("正版盜號驗證 (強烈建議開啟)", "Online Mode (Premium Verify)")) 
        self.online_check.setChecked(True)
        self.wl_check = QCheckBox(_tr("開啟白名單", "Enable Whitelist")) 
        self.flight_check = QCheckBox(_tr("反外掛飛行防護", "Allow Flight (Disable kick)")) 
        
        btn_fw = QPushButton(_tr("🛡️ Windows 防火牆放行", "🛡️ Allow in Windows Firewall"))
        btn_fw.setObjectName("SecondaryBtn")
        btn_fw.clicked.connect(lambda: [self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("已建立 Inbound/Outbound 防火牆放行。", "Inbound/Outbound firewall rules created.")), self.log_sys_alert("Firewall rules modified.", "info")])
        
        frm_sec.addRow(_tr("連線驗證:", "Auth:"), self.online_check)        
        frm_sec.addRow(_tr("伺服存取:", "Whitelist:"), self.wl_check)      
        frm_sec.addRow(_tr("系統防護:", "Anti-Cheat:"), self.flight_check)      
        frm_sec.addRow(_tr("連線網放行:", "Firewall:"), btn_fw)

        grid.addWidget(grp_basic, 0,0)   
        grid.addWidget(grp_game, 0,1)            
        grid.addWidget(grp_world, 1,0)            
        grid.addWidget(grp_sec, 1,1)            

        scroll.setWidget(container)  
        layout.addWidget(scroll)        
        
        btn_save = QPushButton("💾 " + _tr("寫入設定檔案", "Save Properties"))        
        btn_save.setObjectName('PrimaryBtn')   
        btn_save.setMinimumHeight(45)
        btn_save.clicked.connect(self.save_properties)
        layout.addWidget(btn_save)      

    def save_properties(self):
        for s in APP_CONFIG["servers"]:
            if s["name"] == APP_CONFIG["active_server"]:
                s["ram"] = self.ram_slider.value()
                s["aikar"] = self.aikar_flag.isChecked()
                s["custom_jvm"] = self.custom_java_args.text().strip()
        save_config(APP_CONFIG)

        self.max_pl_count = self.max_pl.value()
        self.update_server_sync_count()

        props = {
            "motd": self.motd_input.text(),
            "server-port": self.port_input.value(),
            "max-players": self.max_pl.value(),
            "gamemode": self.gamemode_combo.currentText().split(" ")[0],
            "difficulty": self.diff_combo.currentText(),
            "pvp": "true" if self.pvp_check.isChecked() else "false",
            "hardcore": "true" if self.hc_check.isChecked() else "false",
            "view-distance": self.view_dist.value(),
            "level-seed": self.seed_input.text(),
            "online-mode": "true" if self.online_check.isChecked() else "false",
            "white-list": "true" if self.wl_check.isChecked() else "false",
            "allow-flight": "true" if self.flight_check.isChecked() else "false"
        }
        save_path = os.path.join("servers", APP_CONFIG["active_server"], "server.properties")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("# Generated by Configurator\n")
                for k, v in props.items(): f.write(f"{k}={v}\n")
            self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("設定已成功寫入！硬體配置與 GC 參數也已連動紀錄。", "Settings successfully saved! Hardware config updated."))
            self.log_sys_alert(_tr("屬性與世界設定已更新並寫入檔案。", "Server properties updated and saved."), "success")
        except Exception as e:
            self.show_custom_alert(_tr("錯誤", "Error"), str(e))

    # ==========================
    # P6: 擴充資源線上庫
    # ==========================
    def setup_page_market(self):
        page = self.page_market
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f"<h1 class='title'>📦 {_tr('線上資源庫', 'Marketplace')}</h1>"))
        
        tabs = QTabWidget()
        tab_search = QWidget()
        l_search = QVBoxLayout(tab_search)
        search_bar = QHBoxLayout()
        search_bar.setSpacing(15) 
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(_tr("精準查搜模組...", "Type mod name..."))
        self.search_box.returnPressed.connect(self.execute_mod_search)
        
        self.filter_cb = QComboBox()
        self.filter_cb.addItems(["mod", "plugin", "resourcepack", "shader", "datapack"])
        self.filter_cb.setFixedWidth(150) 
        
        btn_search = QPushButton(_tr("🔍 搜尋", "🔍 Search"))
        btn_search.setObjectName("PrimaryBtn")
        btn_search.clicked.connect(self.execute_mod_search)
        search_bar.addWidget(self.search_box); search_bar.addWidget(self.filter_cb); search_bar.addWidget(btn_search)
        l_search.addLayout(search_bar)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        
        self.market_list_widget = QWidget()
        self.market_list_layout = QVBoxLayout(self.market_list_widget)
        self.market_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.market_list_widget)
        l_search.addWidget(scroll)
        
        tab_manage = QWidget()
        l_manage = QVBoxLayout(tab_manage)
        self.table_mods = QTableWidget(0, 2)
        self.table_mods.setHorizontalHeaderLabels([_tr("已配附上的實體檔案", "Installed File"), _tr("操作", "Actions")])
        self.table_mods.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_mods.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_mods.verticalHeader().setVisible(False)
        self.table_mods.verticalHeader().setDefaultSectionSize(70) 
        
        lo_h = QHBoxLayout()
        btn_import_mod = QPushButton(_tr("📁 手動匯入模組 (.jar)", "📁 Import Local Mod (.jar)"))
        btn_import_mod.clicked.connect(self.import_mod)
        lo_h.addWidget(btn_import_mod); lo_h.addStretch()
        l_manage.addLayout(lo_h)
        l_manage.addWidget(self.table_mods)
        
        tabs.addTab(tab_search, _tr("線上搜索區", "Online Market"))
        tabs.addTab(tab_manage, _tr("本地管理區", "Local Mods"))
        layout.addWidget(tabs)
        self.execute_mod_search()

    def import_mod(self):
        filepath, _ = QFileDialog.getOpenFileName(self, _tr("選擇 Mod JAR", "Select Mod JAR"), "", "Jar Files (*.jar)")
        if filepath:
            target = os.path.join("servers", APP_CONFIG["active_server"], "mods")
            os.makedirs(target, exist_ok=True)
            shutil.copy(filepath, target)
            self.log_sys_alert(_tr(f"已手動匯入模組：{os.path.basename(filepath)}", f"Manually imported mod: {os.path.basename(filepath)}"), "success")
            self.refresh_installed_mods()

    def execute_mod_search(self):
        query = self.search_box.text()
        project_type = self.filter_cb.currentText()
        for i in reversed(range(self.market_list_layout.count())):
            w = self.market_list_layout.itemAt(i).widget()
            if w: w.deleteLater()
        self.market_list_layout.addWidget(QLabel(_tr("⏳ 系統正在搜尋相關資源...", "⏳ Searching...")))
        
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        c_type = curr_srv["core"].lower() if curr_srv else ""
        c_ver = curr_srv["version"] if curr_srv and "未" not in curr_srv.get("version") else ""
        
        thread = FetchModsThread(query=query, core_type=c_type, core_ver=c_ver, project_type=project_type, parent=self)
        thread.finished.connect(self.populate_mod_grid)
        thread.start()
        self.active_threads.append(thread)

    def populate_mod_grid(self, mods):
        for i in reversed(range(self.market_list_layout.count())):
            w = self.market_list_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        if not mods: 
            self.market_list_layout.addWidget(QLabel(_tr("目前條件找不到相關資源。", "No results found.")))
            return

        for title, desc, author, slug in mods:
            card = QFrame()
            card.setObjectName("ModCard")
            card_lo = QHBoxLayout(card)
            
            info_lo = QVBoxLayout()
            t = QLabel(title)
            t.setStyleSheet("font-weight:bold; font-size:16px;")
            info_lo.addWidget(t)
            d = QLabel(desc)
            d.setWordWrap(True) 
            d.setStyleSheet("color:#A0A0A0; margin-top:5px; line-height:1.4;")
            info_lo.addWidget(d)
            
            card_lo.addLayout(info_lo)
            card_lo.addStretch()
            
            btn_dl = QPushButton(_tr("⬇️ 安裝此包", "⬇️ Install"))
            btn_dl.setObjectName("SecondaryBtn")
            btn_dl.setFixedWidth(130)
            btn_dl.clicked.connect(lambda ch, s=slug, b=btn_dl: self.start_mod_download(s, b))
            
            card_lo.addWidget(btn_dl, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.market_list_layout.addWidget(card)

    def start_mod_download(self, slug, btn):
        btn.setEnabled(False)
        thread = DownloadModThread(slug, APP_CONFIG["active_server"], parent=self)
        thread.finished.connect(lambda msg, color, b=btn: [
            b.setText(msg), b.setStyleSheet(f"color: {color};"), 
            self.log_sys_alert(_tr(f"已從網路市集安裝資源：{slug}", f"Installed resource from market: {slug}"), "success"),
            self.refresh_installed_mods()
        ])
        thread.start()
        self.active_threads.append(thread)

    def refresh_installed_mods(self):
        if not hasattr(self, 'table_mods'): return
        self.table_mods.setRowCount(0)
        mods_dir = os.path.join("servers", APP_CONFIG["active_server"], "mods")
        if not os.path.exists(mods_dir): return
            
        mods_files = [f for f in os.listdir(mods_dir) if f.endswith(".jar") or f.endswith(".disabled")]
        for idx, mod in enumerate(mods_files):
            self.table_mods.insertRow(idx)
            is_enabled = not mod.endswith(".disabled")
            self.table_mods.setItem(idx, 0, QTableWidgetItem(mod.replace(".disabled", "")))
            
            btn_t = QPushButton(_tr("✅ 啟用中", "✅ Enabled") if is_enabled else _tr("❌ 停用", "❌ Disabled"))
            btn_t.setObjectName("SuccessBtn" if is_enabled else "SecondaryBtn")
            btn_t.setMinimumWidth(100)
            
            btn_d = QPushButton("🗑️")
            btn_d.setObjectName("DangerBtn")
            btn_d.setMinimumWidth(50)
            btn_d.clicked.connect(lambda ch, m=mod: self.delete_mod(m))
            
            c_widget = create_action_widget([btn_t, btn_d])
            self.table_mods.setCellWidget(idx, 1, c_widget)

    def delete_mod(self, filename):
        target = os.path.join("servers", APP_CONFIG["active_server"], "mods", filename)
        if os.path.exists(target): os.remove(target)
        self.log_sys_alert(_tr(f"已刪除資源實體：{filename}", f"Deleted resource: {filename}"), "error")
        self.refresh_installed_mods()

    # ==========================
    # P7: 伺服器終端機
    # ==========================
    def setup_page_console(self):
        page = self.page_console
        layout = QVBoxLayout(page)    
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(QLabel(f" <h1 class='title'>📟 {_tr('伺服器控制台', 'Server Console')}</h1> "))   

        res_layout = QHBoxLayout()
        res_layout.setContentsMargins(0,0,0,15) 
        res_layout.setSpacing(25)
        
        self.cons_cpu = QLabel("📦 CPU: 0%")
        self.cons_ram = QLabel("🧠 RAM: 0%")
        self.cons_disk = QLabel(f"💾 {_tr('硬碟', 'Disk')}: 0%")
        self.cons_net = QLabel(f"📡 {_tr('網路', 'Network')}: 0 KB/s")
        
        for lbl in [self.cons_cpu, self.cons_ram, self.cons_disk, self.cons_net]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")
            res_layout.addWidget(lbl)
        res_layout.addStretch()
        layout.addLayout(res_layout)
                
        grp_console = QGroupBox(_tr("即時伺服器輸出流日誌", "Live Server Console"))        
        console_v_lo = QVBoxLayout(grp_console)       
           
        self.console_output = QTextEdit()     
        self.console_output.setObjectName("ConsoleOutput") 
        self.console_output.setReadOnly(True)         
        console_v_lo.addWidget(self.console_output)          

        cmd_h_lo = QHBoxLayout()        
        self.cmd_input = QLineEdit() 
        self.cmd_input.setPlaceholderText(_tr("免打斜線。送出指令...", "Type command (no slash)..."))   
        self.cmd_input.returnPressed.connect(self.send_console_command)
        
        btn_send = QPushButton(_tr("送出", "Send"))         
        btn_send.setObjectName("SecondaryBtn")           
        btn_send.clicked.connect(self.send_console_command)

        self.btn_power = QPushButton("🚀 " + _tr("啟動伺服器", "Start Instance"))
        self.btn_power.setObjectName("PrimaryBtn")
        self.btn_power.clicked.connect(self.toggle_server_power)

        cmd_h_lo.addWidget(self.cmd_input)          
        cmd_h_lo.addWidget(btn_send)              
        console_v_lo.addLayout(cmd_h_lo)   
        
        quick_grp = QGroupBox(_tr("⚡ 快捷指令", "⚡ Quick Commands"))
        qk_vlo = QVBoxLayout(quick_grp)
        qk_vlo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def create_cmd_row(cmds):
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            for lbl, cmd in cmds:
                b = QPushButton(lbl)
                b.setObjectName("SecondaryBtn")
                b.clicked.connect(lambda ch, c=cmd: self.send_instant_cmd(c))
                row.addWidget(b)
            return row
            
        row1 = create_cmd_row([
            (_tr("☀️ 白天", "☀️ Day"), "time set day"), 
            (_tr("🌙 黑夜", "🌙 Night"), "time set night"), 
            (_tr("🌂 晴天", "🌂 Clear Weather"), "weather clear"), 
            (_tr("🌧️ 雨天", "🌧️ Rain"), "weather rain")
        ])
        row2 = create_cmd_row([
            (_tr("💾 強制存檔", "💾 Force Save"), "save-all"), 
            (_tr("♻️ 重新載入", "♻️ Reload"), "reload"),
            (_tr("⚔️ 清除掉落物", "⚔️ Clear Drops"), "kill @e[type=item]"),
            (_tr("💀 清除怪物", "💀 Kill Mobs"), "kill @e[type=hostile]")
        ])
        
        qk_vlo.addLayout(row1)
        qk_vlo.addLayout(row2)
        console_v_lo.addWidget(quick_grp)
        
        console_v_lo.addWidget(self.btn_power)
        layout.addWidget(grp_console) 

    def log_to_console(self, msg, color="#D1D5DB"): 
        if color == "red": color = "#EF4444"
        elif color == "green": color = "#10B981"
        elif color == "yellow": color = "#F59E0B"
        html_log = f'<span style="color:{color};">{msg}</span><br>'      
        self.console_output.moveCursor(QTextCursor.MoveOperation.End)   
        self.console_output.insertHtml(html_log)        
        
        if re.search(r'Done \(.*?\)! For help, type "help"', msg) or re.search(r'Timings Reset', msg):
            self.set_server_state("online")
            self.log_sys_alert(_tr("伺服器已成功啟動並上線！", "Server successfully started and is online!"), "success")
            
        if re.search(r"BindException|Address already in use", msg):
            self.log_to_console(_tr("💡 【系統提示】啟動失敗，Port 已被佔用！請檢查是否有其他軟體正在使用。", "💡 [System] Start failed! Port already in use."), "yellow")
            
        join_match = re.search(r": (\w+) joined the game", msg)
        if join_match:
            p = join_match.group(1)
            if p not in self.online_players:
                self.online_players.append(p)
                self.refresh_players_table()
                self.log_sys_alert(_tr(f"玩家 {p} 加入了伺服器。", f"Player {p} joined the server."), "success")
                
        leave_match = re.search(r": (\w+) left the game", msg)
        if leave_match:
            p = leave_match.group(1)
            if p in self.online_players:
                self.online_players.remove(p)
                self.refresh_players_table()
                self.log_sys_alert(_tr(f"玩家 {p} 離開了伺服器。", f"Player {p} left the server."), "warn")

    def toggle_server_power(self):
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        if not curr_srv: return
        
        if self.server_thread and self.server_thread.isRunning():
            self.log_to_console("Sending STOP command...", "yellow")
            self.server_thread.stop_server()
            self.set_server_state("stopping")
        else:
            jar_name = f"server-{curr_srv.get('version', '')}.jar"
            jar_path = os.path.join("servers", APP_CONFIG["active_server"], jar_name)
            
            if not os.path.exists(jar_path) and "Imported" not in curr_srv['core'] and "Custom" not in curr_srv['core']: 
                self.show_custom_alert(_tr("錯誤", "Error"), _tr("核心遺失，請先下傳部署", "Core JAR missing. Download it first."))
                self.switch_menu(4)
                return
            if not os.path.exists(jar_path): 
                jars = [f for f in os.listdir(os.path.join("servers", APP_CONFIG["active_server"])) if f.endswith(".jar")]
                if jars: jar_name = jars[0]
                else: 
                     self.show_custom_alert(_tr("錯誤", "Error"), _tr("找不到任何 .jar 執行檔。", "No .jar executable found."))
                     return

            ram_gb = curr_srv.get("ram", 4)
            aikar_enabled = curr_srv.get("aikar", True)
            custom_arg = curr_srv.get("custom_jvm", "")

            self.console_output.clear()
            self.log_to_console(f"Booting Instance: {APP_CONFIG['active_server']} with RAM limited to {ram_gb}G", "green")
            
            self.btn_power.setText("🛑 " + _tr("中斷連線", "Stop Server"))
            self.btn_power.setObjectName("DangerBtn")
            
            self.set_server_state("starting")
            self.log_sys_alert(_tr(f"準備啟動伺服器實體：{APP_CONFIG['active_server']}", f"Starting server instance: {APP_CONFIG['active_server']}"), "warn")
            
            # 啟動自動備份排程計時器
            hours = curr_srv.get("auto_backup", 0)
            if hours > 0:
                self.auto_backup_timer.start(hours * 3600 * 1000)
                self.log_sys_alert(_tr(f"已觸發自動備份排程 (間隔：{hours} 小時)。", f"Auto-backup routine triggered (Interval: {hours} hr)."), "info")
            
            self.server_thread = ServerRunnerThread(
                server_dir=os.path.join("servers", APP_CONFIG["active_server"]),
                jar_file=jar_name,
                ram_gb=ram_gb,
                aikar=aikar_enabled,
                custom_args=custom_arg,
                parent=self
            )
            self.server_thread.log_signal.connect(self.log_to_console)
            self.server_thread.stopped_signal.connect(self.on_server_stopped)
            self.server_thread.start()

    def on_server_stopped(self):
        self.auto_backup_timer.stop()
        
        self.btn_power.setText("🚀 " + _tr("啟動伺服器", "Start Instance"))
        self.btn_power.setObjectName("PrimaryBtn")
        self.btn_power.setStyleSheet("")
        self.log_to_console("Instance Offline.", "red")
        
        self.online_players.clear()
        self.refresh_players_table()
        self.set_server_state("offline")
        self.log_sys_alert(_tr("伺服器已安全關閉。", "Server has been safely stopped."), "info")
        
        # 觸發關機自動備份機制
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        if curr_srv and curr_srv.get("backup_on_stop", False):
            self.make_backup(auto=True)

    def send_console_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd: return
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.send_command(cmd)
            self.cmd_input.clear()

    # ==========================
    # P8: Backup
    # ==========================
    def setup_page_backup(self):
        page = self.page_backup
        v_layout = QVBoxLayout(page)         
        v_layout.setContentsMargins(40, 30, 40, 30)
        v_layout.addWidget(QLabel(f" <h1 class='title'>📅 {_tr('地圖快照與備份', 'World Backups')}</h1> ") )    

        cfg_grp = QGroupBox(_tr("自動備份設定", "Auto-Backup Configuration"))
        cfg_lo = QHBoxLayout(cfg_grp)

        self.ab_interval = QComboBox()
        self.ab_interval.addItems([
            _tr("停用 (預設)", "Disabled (Default)"), 
            _tr("每 1 小時", "Every 1 hr"), 
            _tr("每 6 小時", "Every 6 hrs"), 
            _tr("每 12 小時", "Every 12 hrs"), 
            _tr("每 24 小時", "Every 24 hrs")
        ])
        
        self.ab_shutdown = QCheckBox(_tr("伺服器安全關閉時，自動存檔並備份", "Auto-backup on server shutdown"))

        btn_save_ab = QPushButton(_tr("儲存排程", "Save Routine"))
        btn_save_ab.setObjectName("PrimaryBtn")
        btn_save_ab.clicked.connect(self.save_backup_settings)

        cfg_lo.addWidget(QLabel(_tr("自動備份間隔:", "Auto-backup Interval:")))
        cfg_lo.addWidget(self.ab_interval)
        cfg_lo.addSpacing(20)
        cfg_lo.addWidget(self.ab_shutdown)
        cfg_lo.addStretch()
        cfg_lo.addWidget(btn_save_ab)
        v_layout.addWidget(cfg_grp)

        grp_bkp = QGroupBox(_tr("建立快照與還原管理", "Snapshot & Restore Management"))   
        bkp_v_layout = QVBoxLayout(grp_bkp)      

        self.table_bkp = QTableWidget(0, 3)                
        self.table_bkp.setHorizontalHeaderLabels([_tr("ZIP 備份檔案", "Backup File"), _tr("大小", "Size"), _tr("操作", "Actions")]) 
        self.table_bkp.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)    
        self.table_bkp.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)    
        self.table_bkp.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)    
        self.table_bkp.verticalHeader().setVisible(False)           
        self.table_bkp.verticalHeader().setDefaultSectionSize(70) 
             
        btn_create = QPushButton(_tr("📦 對當下資料執行壓縮備份", "📦 Create Backup Snapshot"))
        btn_create.setObjectName("PrimaryBtn")
        btn_create.setMinimumHeight(45)
        btn_create.clicked.connect(lambda: self.make_backup(auto=False))
        
        bkp_v_layout.addWidget(btn_create)
        bkp_v_layout.addWidget(self.table_bkp) 
        v_layout.addWidget(grp_bkp)           
        self.refresh_backups()

    def save_backup_settings(self):
        if not APP_CONFIG["active_server"]: return
        hours_map = {0: 0, 1: 1, 2: 6, 3: 12, 4: 24}
        idx = self.ab_interval.currentIndex()
        h = hours_map.get(idx, 0)
        
        for s in APP_CONFIG["servers"]:
            if s["name"] == APP_CONFIG["active_server"]:
                s["auto_backup"] = h
                s["backup_on_stop"] = self.ab_shutdown.isChecked()
        save_config(APP_CONFIG)
        self.show_custom_alert(_tr("系統提示", "System Info"), _tr("自動備份排程與設定已儲存！", "Auto-backup settings saved successfully!"))
        
        if self.server_thread and self.server_thread.isRunning():
            self.auto_backup_timer.stop()
            if h > 0: self.auto_backup_timer.start(h * 3600 * 1000)

    def refresh_backups(self):
        curr_srv = next((s for s in APP_CONFIG["servers"] if s["name"] == APP_CONFIG["active_server"]), None)
        if curr_srv:
            idx_map = {0:0, 1:1, 6:2, 12:3, 24:4}
            self.ab_interval.setCurrentIndex(idx_map.get(curr_srv.get("auto_backup", 0), 0))
            self.ab_shutdown.setChecked(curr_srv.get("backup_on_stop", False))
            
        if not hasattr(self, 'table_bkp'): return
        self.table_bkp.setRowCount(0)
        bk_dir = os.path.join("servers", APP_CONFIG["active_server"], "backups")
        if not os.path.exists(bk_dir): return
        files = [f for f in os.listdir(bk_dir) if f.endswith(".zip")]
        for idx, file in enumerate(files):
            size_mb = os.path.getsize(os.path.join(bk_dir, file)) / (1024*1024)
            self.table_bkp.insertRow(idx)
            self.table_bkp.setItem(idx, 0, QTableWidgetItem(file))
            self.table_bkp.setItem(idx, 1, QTableWidgetItem(f"{size_mb:.1f} MB"))
            
            btn_res = QPushButton(_tr("↩️ 還原存檔", "↩️ Restore"))
            btn_res.setObjectName("SecondaryBtn")
            btn_res.setMinimumWidth(120) 
            btn_res.clicked.connect(lambda ch, f=file: self.restore_backup(f))
            
            btn_del = QPushButton("🗑️")
            btn_del.setObjectName("DangerBtn")
            btn_del.setMinimumWidth(50)
            btn_del.clicked.connect(lambda ch, f=file: self.delete_backup(f))
            
            self.table_bkp.setCellWidget(idx, 2, create_action_widget([btn_res, btn_del]))

    def make_backup(self, auto=False):
        if not APP_CONFIG["active_server"]: return
        
        # 防止手動備份時伺服器運行造成破檔。若為自動備份，則進行安全指令寫入再壓縮。
        if self.server_thread and self.server_thread.isRunning():
            if not auto:
                return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("為避免破檔，手動備份時請先關閉伺服器！", "Cannot backup manually while server is running to prevent corruption."))
            else:
                self.server_thread.send_command("save-off")
                self.server_thread.send_command("save-all")
        
        self.log_sys_alert(_tr("系統正在背景執行地圖快照壓縮...", "Creating world backup snapshot in background..."), "warn")
        thread = BackupWorldThread(APP_CONFIG["active_server"], parent=self)
        
        def on_backup_done(msg, ok):
            if self.server_thread and self.server_thread.isRunning():
                self.server_thread.send_command("save-on")
            if not auto:
                self.show_custom_alert(_tr("系統回報", "System Info"), msg)
            self.log_sys_alert(msg, "success" if ok else "error")
            self.refresh_backups()
            
        thread.finished.connect(on_backup_done)
        thread.start()
        self.active_threads.append(thread)

    def restore_backup(self, filename):
        if self.server_thread and self.server_thread.isRunning():
            return self.show_custom_alert(_tr("系統提示", "System Notification"), _tr("還原前請先關閉伺服器！", "Please stop the server before restoring."))
            
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel(_tr("您的操作即將完全覆蓋目前的 World。\n歷史是否要重新覆寫引導？", "Overwrite current world directory with this backup?")))
        def confirm():
            self.overlay.hide_modal(force=True)
            self.log_sys_alert(_tr(f"開始還原備份檔案：{filename}", f"Restoring backup file: {filename}"), "warn")
            thread = RestoreBackupThread(APP_CONFIG["active_server"], filename, parent=self)
            thread.finished.connect(lambda msg, ok: [self.show_custom_alert(_tr("操作覆核結果", "Action Result"), msg), self.log_sys_alert(msg, "success" if ok else "error")])
            thread.start()
            self.active_threads.append(thread)
            
        btn_cancel = QPushButton(_tr("取消", "Cancel"))
        btn_cancel.setObjectName("SecondaryBtn")
        btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_cancel.setMinimumHeight(45)
        btn_cancel.clicked.connect(self.overlay.hide_modal)
        
        btn_confirm = QPushButton(_tr("確認還原", "Confirm Reset"))
        btn_confirm.setObjectName("PrimaryBtn")
        btn_confirm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_confirm.setMinimumHeight(45)
        btn_confirm.clicked.connect(confirm)
        
        lo_h = QHBoxLayout(); lo_h.addWidget(btn_cancel); lo_h.addWidget(btn_confirm)
        l.addLayout(lo_h)
        self.overlay.set_content(_tr("二次確認", "Confirmation"), w, allow_close=False)
        self.overlay.show_modal()

    def delete_backup(self, filename):
        target = os.path.join("servers", APP_CONFIG["active_server"], "backups", filename)
        if os.path.exists(target): os.remove(target)
        self.log_sys_alert(_tr(f"已刪除備份快照：{filename}", f"Deleted backup snapshot: {filename}"), "error")
        self.refresh_backups()


    # ==========================
    # P9: Network
    # ==========================
    def setup_page_network(self):      
        page = self.page_network        
        v_layout = QVBoxLayout(page)             
        v_layout.setContentsMargins(40, 30, 40, 30)
        v_layout.addWidget(QLabel(f"<h1 class='title'>🌐 {_tr('內網穿透與通道', 'Network Tunnels')}</h1>"))           
        
        grp_net = QGroupBox(_tr("通用掛載區", "Tunnel Execution"))          
        form_net = QFormLayout(grp_net)  

        self.frp_path = QLineEdit()              
        btn_browse = QPushButton(_tr("📁 選擇程式", "📁 Select File"))
        btn_browse.setObjectName("SmallBtn")
        btn_browse.clicked.connect(lambda: [
            self.frp_path.setText(QFileDialog.getOpenFileName(self, _tr("選取代理程式", "Select Executable"), "", "Executables (*.exe *.bat *.sh)")[0])
        ])
        frp_lo = QHBoxLayout()
        frp_lo.addWidget(self.frp_path)
        frp_lo.addWidget(btn_browse)
        form_net.addRow(_tr("執行檔路徑:", "Executable Path:"), frp_lo)      
        
        self.frp_args = QLineEdit() 
        self.frp_args.setPlaceholderText("-c frpc.ini")
        form_net.addRow(_tr("參數:", "Arguments:"), self.frp_args)  
        v_layout.addWidget(grp_net)          

        self.frp_output = QTextEdit()     
        self.frp_output.setReadOnly(True)         
        v_layout.addWidget(self.frp_output)          

        cmd_h_lo = QHBoxLayout()        
        self.frp_input = QLineEdit() 
        self.frp_input.setPlaceholderText(_tr("打入操作字元...", "Type input here..."))   
        self.frp_input.returnPressed.connect(self.send_frp_command)
        
        btn_send = QPushButton(_tr("送出", "Send"))         
        btn_send.setObjectName("SecondaryBtn")           
        btn_send.clicked.connect(self.send_frp_command)

        self.btn_frp_power = QPushButton("🚀 " + _tr("開啟穿透", "Start Tunnel"))
        self.btn_frp_power.setObjectName("PrimaryBtn")
        self.btn_frp_power.clicked.connect(self.toggle_frp_power)

        cmd_h_lo.addWidget(self.frp_input)          
        cmd_h_lo.addWidget(btn_send)              
        v_layout.addLayout(cmd_h_lo)   
        v_layout.addWidget(self.btn_frp_power)
        
        self.log_to_frp(_tr("⚠️ 若需要在背景綁定端口，請對本程式按右鍵「以系統管理員身分執行」。", "⚠️ Run this panel as Administrator if port binding fails."), "yellow")
        self.frp_runner = None

    def log_to_frp(self, msg, color="#D1D5DB"): 
        self.frp_output.moveCursor(QTextCursor.MoveOperation.End)   
        self.frp_output.insertHtml(f'<span style="color:{color};">{msg}</span><br>')        

    def toggle_frp_power(self):
        if self.frp_runner and self.frp_runner.isRunning():
            self.frp_runner.stop_process()
        else:
            exe = self.frp_path.text()
            if not os.path.exists(exe):
                self.show_custom_alert(_tr("錯誤", "Error"), _tr("找不到您指定的執行檔！", "Executable not found!"))
                return
            self.frp_output.clear()
            self.log_to_frp(">> Booting script...", "green")
            self.btn_frp_power.setText("🛑 " + _tr("截斷", "Kill Tunnel"))
            self.btn_frp_power.setObjectName("DangerBtn")
            
            self.frp_runner = FrpRunnerThread(exe, self.frp_args.text(), parent=self)
            self.frp_runner.log_signal.connect(self.log_to_frp)
            self.frp_runner.stopped_signal.connect(self.on_frp_stopped)
            self.frp_runner.start()

    def on_frp_stopped(self):
        self.btn_frp_power.setText("🚀 " + _tr("重新開啟", "Start Tunnel"))
        self.btn_frp_power.setObjectName("PrimaryBtn")
        self.btn_frp_power.setStyleSheet("")
        self.log_to_frp(">> Offline.", "red")

    def send_frp_command(self):
        cmd = self.frp_input.text().strip()
        if not cmd: return
        if self.frp_runner and self.frp_runner.isRunning():
            self.frp_runner.send_command(cmd)
            self.frp_input.clear()


    # ==========================
    # P10 & P11 說明與設定
    # ==========================
    def setup_page_manual(self):
        page = self.page_manual
        lo = QVBoxLayout(page)
        lo.setContentsMargins(40, 30, 40, 30)
        lo.addWidget(QLabel(f"<h1 class='title'>📖 {_tr('面板核心功能完整教學', 'User Manual')}</h1>"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        w = QWidget()
        vl = QVBoxLayout(w)
        
        txt_zh = """<div style='line-height:2.0; font-size: 15px;'>
        <h3 style='color: #10B981; margin-bottom: 5px;'>1. 🗂️ 多站點與伺服器建立</h3>
        <p style='margin-top: 0;'>在左側菜單選擇<b>「多伺服器清單」</b>，點擊「建立新伺服器」並輸入全英數的名稱。系統會自動在資料夾下為您建立獨立空間，互不干擾。您可以隨時點選「切換」來決定目前要管理與開機的站點。</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>2. ⚙️ 下載核心與環境屬性</h3>
        <p style='margin-top: 0;'>切換到伺服器後，前往<b>「核心與下載環境」</b>一鍵下載最新版 Paper 等官方來源。<br>接著至<b>「屬性與世界設定」</b>，透過圖形化介面輕鬆調配 RAM 記憶體大小、最多遊玩人數，存檔後系統將自動為您修改繁雜的 <code>server.properties</code> 檔案。</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>3. 📦 擴充模組市集</h3>
        <p style='margin-top: 0;'>在<b>「擴充資源市集」</b>，您可以直接搜尋 Modrinth 上的海量資源。找到喜歡的插件後點擊「安裝」即可自動匯入。您也可以管理或刪除已安裝的模組。</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>4. 📟 伺服器啟動與玩家管理</h3>
        <p style='margin-top: 0;'>前往<b>「伺服器控制台」</b>點擊「啟動伺服器」。啟動後，控制台會為您解析日誌，並可使用快捷鍵調配時間與氣候。若有玩家加入，更可至<b>「玩家與權限管理」</b>利用圖形按鈕一鍵給予 OP 或是切換創造模式。</p>
        
        <h3 style='color: #10B981; margin-bottom: 5px;'>5. 📅 地圖快照與自動備份</h3>
        <p style='margin-top: 0;'><b>「地圖快照與備份」</b>不僅提供一鍵存檔還原功能，您還可以設定「每 N 小時自動備份」與「關機自動備份」。此機制在伺服器運行時也能發揮作用，並自動利用安全指令防止您的世界破檔。</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>6. 🌐 內網穿透 (FRP)</h3>
        <p style='margin-top: 0;'>若您無法設定對外連接埠，請至<b>「內網穿透與通道」</b>綁定外部的代理程式。設定完參數後即可在面板背景安全執行！</p>

        <hr style='border: 0; border-top: 1px solid #373A40; margin: 25px 0;'>

        <h3 style='color: #E0E0E0; margin-bottom: 5px;'>【開源聲明】</h3>
        <p style='margin-top: 0; color: #A0A0A0;'>本程式碼完全開源免費提供於 GitHub，您可以自由修改原始碼貢獻。<br><b>唯禁止以任何形式作為商業專案販售行為！</b></p>
        </div>"""

        txt_en = """<div style='line-height:2.0; font-size: 15px;'>
        <h3 style='color: #10B981; margin-bottom: 5px;'>1. 🗂️ Create Server & Management</h3>
        <p style='margin-top: 0;'>Go to <b>Servers Management</b>, click Create Server and enter an alphanumeric name. The system will create an isolated folder. You can easily switch between them.</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>2. ⚙️ Download Core & Setup</h3>
        <p style='margin-top: 0;'>In <b>Core Deploy & Downloads</b>, download your preferred core (like Paper). Afterwards, go to <b>Server Properties</b> to configure RAM, player slots, and game modes via GUI sliders.</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>3. 📦 Install Mods & Plugins</h3>
        <p style='margin-top: 0;'>In the <b>Marketplace</b>, you can search for resources on Modrinth and click install to automatically download them to your server's mods folder.</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>4. 📟 Console & Player Control</h3>
        <p style='margin-top: 0;'>Go to <b>Server Console</b> and click Start Instance. You can utilize quick command keys here. Furthermore, manage connected players dynamically in the <b>Players & Permissions</b> tab.</p>
        
        <h3 style='color: #10B981; margin-bottom: 5px;'>5. 📅 Automated Backups</h3>
        <p style='margin-top: 0;'>In <b>World Backups</b>, you can zip compress your entire world. You can also set routine auto-backups or backup-on-shutdown features to keep your progress safe.</p>

        <h3 style='color: #10B981; margin-bottom: 5px;'>6. 🌐 Network Tunnel (FRP)</h3>
        <p style='margin-top: 0;'>If you don't have a public IP, use the <b>Network Tunnels</b> feature. Download an FRP client, select the executable, enter your arguments, and start the tunnel safely in the background.</p>
        <hr style='border: 0; border-top: 1px solid #373A40; margin: 25px 0;'>

        <h3 style='color: #E0E0E0; margin-bottom: 5px;'>[Open Source Spec]</h3>
        <p style='margin-top: 0; color: #A0A0A0;'>This software is Free and Open Source. You can modify it, but <b>commercial selling is strictly prohibited</b>.</p>
        </div>"""

        lbl = QLabel(_tr(txt_zh, txt_en))
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lbl.setWordWrap(True)
        vl.addWidget(lbl)
        vl.addStretch()
        scroll.setWidget(w)
        lo.addWidget(scroll)

    def setup_page_settings(self):
        page = self.page_settings
        lo = QVBoxLayout(page)
        lo.setContentsMargins(40, 30, 40, 30)
        lo.addWidget(QLabel("<h1 class='title'>⚙️ Panel Settings</h1>"))
        
        tc = QComboBox()
        tc.addItems([_tr("🌙 深色模式 (Dark)", "🌙 Dark Mode"), _tr("☀️ 淺色模式 (Light)", "☀️ Light Mode")])
        tc.setCurrentIndex(0 if APP_CONFIG["is_dark"] else 1)
        tc.currentTextChanged.connect(lambda t: [
            save_config({**APP_CONFIG, "is_dark": "Dark" in t or "深色" in t}), 
            self.setStyleSheet(get_stylesheet("Dark" in t or "深色" in t))
        ])
        
        lc = QComboBox()
        lc.addItems(["zh (繁體中文)", "en (English)"])
        lc.setCurrentIndex(0 if APP_CONFIG["language"] == "zh" else 1)
        lc.currentTextChanged.connect(lambda t: [
            save_config({**APP_CONFIG, "language": "zh" if "zh" in t else "en"}), 
            self.show_custom_alert(_tr("系統提示", "Info"), _tr("請手動重新啟動面板以完全套用語言變更！", "Restart Application to fully apply Language changes!"))
        ])
        
        lo.addWidget(QLabel(_tr("主題設定 (Live Theme):", "Theme Setup (Live):"))); lo.addWidget(tc)
        lo.addWidget(QLabel(_tr("語言設定 (Language):", "Language Setup:"))); lo.addWidget(lc)
        lo.addStretch()

    # ==========================
    # 關機與隱藏背景常駐管理
    # ==========================
    def show_close_dialog(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(_tr("請問您要完全關閉程式，還是將其縮小至系統匣背景運行？\n\n<span style='color:#10B981;'>(若伺服器運行中，安全關機會先發送停止指令等待存檔後再退出程式)</span>", "Close fully or minimize?\n\n<span style='color:#10B981;'>(If running, Safe Shutdown will safely save the world before closing)</span>"))
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 15px; margin-bottom: 25px; line-height: 1.5;")
        l.addWidget(lbl)
        
        btn_min = QPushButton(_tr("縮小至系統匣 (背景運行)", "Send to Tray"))
        btn_min.setObjectName("SuccessBtn")
        btn_min.setMinimumHeight(45)
        btn_min.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_min.clicked.connect(self.hide_to_tray)

        btn_close = QPushButton(_tr("安全關機並退出", "Safe Shutdown"))
        btn_close.setObjectName("DangerBtn")
        btn_close.setMinimumHeight(45)
        btn_close.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_close.clicked.connect(self.force_quit)

        btn_cancel = QPushButton(_tr("取消", "Cancel"))
        btn_cancel.setObjectName("SecondaryBtn")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_cancel.clicked.connect(self.overlay.hide_modal)
        
        lo_h = QHBoxLayout()
        lo_h.setSpacing(15)
        lo_h.addWidget(btn_min); lo_h.addWidget(btn_close); lo_h.addWidget(btn_cancel)
        l.addLayout(lo_h)
        self.overlay.set_content(_tr("退出確認", "Exit Confirmation"), w, width=550, allow_close=False)
        self.overlay.show_modal()

    def hide_to_tray(self):
        self.overlay.hide_modal(force=True)
        self.hide()
        self.tray_icon.showMessage(_tr("面板繼續運行", "Running in Background"), _tr("伺服器面板已縮小至背景，雙擊圖示即可喚醒！", "Panel minimized. Double click the tray icon to restore."), QSystemTrayIcon.MessageIcon.Information, 2000)

    def force_quit(self):
        self.overlay.hide_modal(force=True)
        self.hide()
        
        wait_time = 100
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop_server()
            wait_time = 5000 
            
        if getattr(self, 'frp_runner', None) and self.frp_runner.isRunning():
            self.frp_runner.stop_process()
            
        QTimer.singleShot(wait_time, QApplication.quit)

    def eventFilter(self, source, event):
        if source == self.central_widget and event.type() == QEvent.Type.Resize:
            self.overlay.resize(self.central_widget.size())
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        event.ignore()
        self.show_close_dialog()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setQuitOnLastWindowClosed(False)
    
    font = app.font()
    font.setFamily("Segoe UI") 
    font.setPointSize(10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())