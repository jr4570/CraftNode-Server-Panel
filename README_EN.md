# ⚡ CraftNode Server Panel

<p align="center">
  <a href="README.md">繁體中文版</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-GUI-brightgreen.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/License-Open_Source-orange.svg" alt="License">
</p>

---

## 🇺🇸 English

**CraftNode** is a modern, lightweight Minecraft server management panel built with Python and PySide6. It is designed for server owners who need a fast, elegant, and hassle-free way to deploy and manage multiple servers.

It features one-click core downloads, built-in Modrinth integration, live player management, GUI-based server properties, and native support for FRP network tunneling.

### 📸 Dashboard Preview

[![Dashboard Screenshot](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image2.png?raw=true)](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image2.png?raw=true)

### ✨ Features

* **🗂️ Multi-Workspace Management**: Create isolated server directories. Switch between different versions and ecosystems seamlessly without file conflicts.
* **⚙️ One-Click Core Deployment**: Automatically fetch and download the latest builds for Paper, Vanilla, and Fabric. EULA is accepted automatically.
* **🛠️ GUI Server Properties**: Say goodbye to text files. Configure RAM, Aikar's flags, ports, and gameplay settings via intuitive sliders and dropdowns (syncs automatically with `server.properties`).
* **📦 Built-in Modrinth Marketplace**: Search, download, enable, and delete mods/plugins directly within the panel's interface.
* **📟 Live Console & Hardware Monitor**: Real-time server logs integrated with live CPU, RAM, Disk, and Network usage statistics.
* **👥 Player & Permission Control**: Smart parsing of player logins. One-click OP, gamemode switching, kicks, and bans.
* **📅 Snapshot Backups**: One-click ZIP backups for your world data with a built-in safe restore feature.
* **🌐 Network Tunneling (FRP)**: Built-in interactive console for FRP, allowing you to host servers without needing a public IP or port forwarding.
* **🌙 Modern UI & System Tray**: Supports Dark/Light modes, bilingual UI (EN/ZH), and minimizes to the system tray with a Safe Shutdown feature.

### 🚀 Requirements & Installation

**Prerequisites:**
* Python 3.8 or higher.
* The appropriate Java Version required to run your Minecraft server (e.g., Java 17/21 for MC 1.20+).

**1. Clone the repository:**
```bash
git clone [https://github.com/jr4570/CraftNode-Server-Panel.git](https://github.com/jr4570/CraftNode-Server-Panel.git)
cd CraftNode-Server-Panel
```

**2. Install dependencies:**
```bash
pip install PySide6 requests psutil
```

**3. Run the panel:**
```bash
python CraftNode.py
```
*(Optional) To use the Network Tunnel feature, download the FRP Client separately and select the executable in the panel.*

### 📦 Building a Standalone Executable (EXE)

If you wish to package this panel into a standalone Windows executable (`.exe`) that runs without requiring a Python environment installed, you can compile it using **PyInstaller**:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Run the compilation command:**
   Execute the following command in the project root directory:
   ```bash
   pyinstaller --noconsole --onefile --name="CraftNodePanel" CraftNode.py
   ```
   * **`--noconsole`**: Hides the background command prompt window, ensuring a pure graphical GUI experience.
   * **`--onefile`**: Bundles all source files and source dependencies into a single, clean `.exe`.
   * **`--name`**: Sets the file name of your output executable.

3. **Locate the Output File:**
   Once compilation is complete, you can find `CraftNodePanel.exe` inside the newly generated `dist/` directory. Simply double-click the file to launch it independently (it will automatically handle data folders and configs on its first boot).

### 📜 License

This project is free and open-source software. You are free to modify the source code to fit your needs. **However, selling this software as a proprietary commercial product is strictly prohibited.**
