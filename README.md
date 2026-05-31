# ⚡ CraftNode Server Panel

<p align="center">
  <a href="README_EN.md">English Version</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-GUI-brightgreen.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Windows">
  <img src="https://img.shields.io/badge/License-Open_Source-orange.svg" alt="License">
</p>

---

## 🌐 繁體中文

**CraftNode** 是一款基於 Python 與 PySide6 開發的現代化、輕量級 Minecraft 伺服器圖形化管理面板。專為需要快速架設、輕鬆管理多個伺服器的服主所設計。告別繁瑣的指令碼與文字檔，透過直覺的介面全面掌控您的伺服器生態。

### 📸 面板預覽

[![Dashboard Screenshot](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image1.png?raw=true)](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image1.png?raw=true)

---

### ✨ 核心功能模組 (Features)

#### ⚙️ 全域與系統級功能
* **多語系與動態主題**：內建中英雙語無縫切換，支援深色 (Dark) / 淺色 (Light) 模式即時套用。
* **背景常駐與安全關機 (Safe Shutdown)**：支援縮小至系統匣運行。關閉程式時若伺服器運行中，系統會自動攔截並發送 `stop` 指令，等待地圖安全存檔後才完全退出。
* **智慧狀態列**：即時顯示伺服器狀態，自動抓取內/外網 IP，並提供「隱藏 IP (防實況主洩漏)」與一鍵複製功能。

#### 🗄️ 多伺服器站點管理
* **環境完全隔離**：建立無限個伺服器專案，彼此設定、存檔、模組絕對獨立互不干擾。
* **ZIP 一鍵匯入**：支援直接匯入既有的伺服器壓縮包，自動解壓縮並登錄至面板。

#### 🛠️ 核心部署與屬性設定
* **官方 API 連動下載**：即時抓取 Paper, Vanilla, Fabric 版本清單。內建 EULA 授權介面，同意後自動完成部署。
* **圖形化 `server.properties`**：拋棄文字檔！透過拉桿與選單配置遊戲機制、白名單、極限模式。
* **效能與防護一鍵到位**：
  * 拉桿動態分配 RAM 記憶體。
  * 一鍵寫入 **Aikar's GC 最佳化啟動參數**。
  * 呼叫 Windows 底層，一鍵將 25565 Port 加入防火牆允許清單。

#### 📟 伺服器控制台與即時監控
* **互動式終端機**：完整掛載 Java 伺服器運行緒，提供彩色日誌輸出與指令發送。
* **硬體即時監控**：首頁與控制台皆附帶 CPU、RAM、硬碟與網路上下傳 (KB/s) 的即時數據視覺化。
* **快捷指令陣列**：內建 8 個常用管理按鈕（日/夜切換、晴/雨切換、強制存檔、清理掉落物/怪物等）。

#### 👥 玩家與權限管理
* **智慧日誌解析**：精準捕捉底層 Log，動態更新線上玩家名單。
* **圖形化操作**：提供雙排快捷按鈕，一鍵給予/撤銷 OP、切換生存/創造模式，或進行踢出與封鎖（自動附帶中文理由）。

#### 📦 擴充資源市集 (Marketplace)
* **Modrinth 深度整合**：直接在面板內搜尋 Mod、Plugin、材質包與光影，點擊「安裝」自動匯入。
* **本地模組管理**：支援手動匯入 `.jar`，並提供一鍵「停用/啟用」功能（透過 `.disabled` 後綴實現免刪除停用）。

#### 📅 地圖快照與自動備份
* **防破檔備份機制**：背景備份前，面板會自動發送 `save-off` 與 `save-all` 鎖定區塊，確保壓縮檔完整性。
* **彈性排程**：支援手動 ZIP 快照、每 1/6/12/24 小時自動備份，以及「關機自動備份」。
* **一鍵還原**：歷史備份列表一目瞭然，點擊還原即可自動抹除當前世界並解壓縮覆蓋。

#### 📡 內網穿透 (Network Tunnels)
* **通用代理掛載器**：專為 FRP 或 Ngrok 設計，指定 `.exe` 與參數後即可在面板背景安全執行。
* **獨立終端互動**：提供專屬 Log 視窗與輸入框，輕鬆應付需要手動認證的穿透工具。

---

### 🚀 系統需求與安裝 (Installation)

**環境要求：**
* Python 3.8 或以上版本。
* 運行 Minecraft 伺服器所需的 Java 版本（如 MC 1.20+ 需要 Java 17/21）。

**1. 取得程式碼與安裝依賴：**
```bash
git clone [https://github.com/jr4570/CraftNode-Server-Panel.git](https://github.com/jr4570/CraftNode-Server-Panel.git)
cd CraftNode-Server-Panel
pip install PySide6 requests psutil
```

**2. 啟動面板：**
```bash
python CraftNodePanel.py
```

### 📦 下載獨立執行檔 (Installer)
如果您不想安裝 Python 環境，請前往 **[Releases]** 頁面下載最新版的 `CraftNodePanel_Installer.exe`。
* 內建所有依賴，雙擊即可引導安裝。
* 支援安裝過程中自動下載並靜默部署 JDK 26 環境。

### 📜 開源聲明 (License)
本專案為免費開源軟體，您可以自由修改原始碼以符合自身需求。**唯嚴禁將本軟體直接或變相作為私有商業專案進行販售獲利。**
