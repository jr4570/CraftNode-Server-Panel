# ⚡ CraftNode Server Panel

<p align="center">
  <a href="README.md">繁體中文版</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-GUI-brightgreen.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Windows">
  <img src="https://img.shields.io/badge/License-Open_Source-orange.svg" alt="License">
</p>

---

## 🌍 English

**CraftNode** is a modern, lightweight, and modular Minecraft server management panel built with Python and PySide6. Designed for server owners who need a fast and hassle-free way to deploy and manage multiple servers. Say goodbye to tedious scripts and text files—take full control of your server ecosystem through an intuitive UI.

### 📸 Dashboard Preview

[![Dashboard Screenshot](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image2.png?raw=true)](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image2.png?raw=true)

---

### ✨ Core Features

#### ⚙️ Global & System
* **Bilingual & Dynamic Themes**: Seamless switching between English and Traditional Chinese. Supports Dark and Light modes applied instantly.
* **Safe Shutdown & System Tray**: Minimizes to the system tray for silent background execution. If the server is running upon exit, the panel intercepts the close event, sends a `stop` command, and waits for a safe world save before terminating.
* **Smart Status Bar**: Displays real-time server status, auto-fetches Local/Public IP, and includes a "Hide IP" feature (streamer mode) and 1-click copy.

#### 🗄️ Multi-Workspace Management
* **Isolated Environments**: Create unlimited server instances. Each server gets its own dedicated folder, keeping configs, worlds, and mods completely separated.
* **ZIP Import**: Directly import existing server archives (`.zip`). The panel auto-extracts and registers them.

#### 🛠️ Deployment & Properties
* **API-Driven Core Downloader**: Fetches the latest builds for Paper, Vanilla, and Fabric. Features a built-in Mojang EULA acceptance UI.
* **GUI `server.properties`**: No more text editing! Configure gameplay, whitelist, and hardcore mode via sliders and dropdowns.
* **Performance & Security**:
  * Dynamic RAM allocation slider.
  * 1-Click injection of **Aikar's GC Optimization Flags**.
  * 1-Click Windows Firewall rule creation for port 25565.

#### 📟 Console & Live Monitoring
* **Interactive Terminal**: Full integration with the Java server process, offering colored stdout logging and command input.
* **Hardware Monitor**: Real-time visual metrics for CPU, RAM, Disk, and Network (KB/s) usage.
* **Quick-Command Array**: 8 built-in buttons for common tasks (Day/Night, Weather, Force Save, Kill Entities).

#### 👥 Player & Permission Control
* **Smart Log Parsing**: Accurately detects player logins/logouts from the backend to dynamically update the online players list.
* **Action Buttons**: 1-click buttons to OP/De-OP, switch Gamemodes (Survival/Creative), Kick, and Ban.

#### 📦 Marketplace & Modding
* **Modrinth Integration**: Search for Mods, Plugins, Resourcepacks, and Shaders directly within the panel. Click to install natively.
* **Local Mod Management**: Import local `.jar` files. Supports 1-click Enable/Disable (renames to `.disabled` to avoid deletion).

#### 📅 Snapshots & Auto-Backups
* **Anti-Corruption Mechanism**: Before backing up in the background, the panel issues `save-off` and `save-all` to lock chunks, ensuring archive integrity.
* **Flexible Scheduling**: Supports manual ZIP snapshots, auto-backups every 1/6/12/24 hours, and "Backup on Safe Shutdown".
* **1-Click Restore**: View all historical backups and restore them instantly (auto-wipes current world and extracts).

#### 📡 Network Tunnels
* **Universal Proxy Mounter**: Designed for FRP or Ngrok. Specify the `.exe` and arguments, and run your tunnel safely in the panel's background.
* **Dedicated Terminal**: Includes a specific log output and input box for proxy software that requires manual token authentication.

---

### 🚀 Requirements & Installation

**Prerequisites:**
* Python 3.8 or higher.
* The appropriate Java Version required to run your Minecraft server (e.g., Java 17/21 for MC 1.20+).

**1. Clone & Install Dependencies:**
```bash
git clone [https://github.com/jr4570/CraftNode-Server-Panel.git](https://github.com/jr4570/CraftNode-Server-Panel.git)
cd CraftNode-Server-Panel
pip install PySide6 requests psutil
```

**2. Launch the Panel:**
```bash
python CraftNodePanel.py
```

### 📦 Standalone Installer (EXE)
If you prefer not to install Python, head over to the **[Releases]** page and download `CraftNodePanel_Installer.exe`.
* Bundles all dependencies.
* Supports silent auto-installation of JDK 26 during the setup process.

### 📜 License
This project is free and open-source software. You are free to modify the source code to fit your needs. **However, selling this software as a proprietary commercial product is strictly prohibited.**
