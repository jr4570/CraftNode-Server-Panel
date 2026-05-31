# ⚡ CraftNode Server Panel

<p align="center">
  <a href="README_EN.md">English Version</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-GUI-brightgreen.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/License-Open_Source-orange.svg" alt="License">
</p>

---

## 🇹🇼 繁體中文

**CraftNode** 是一款基於 Python 與 PySide6 開發的現代化、輕量級 Minecraft 伺服器圖形化管理面板。專為需要快速架設、輕鬆管理多個伺服器的服主所設計。

我們為您提供了一鍵核心下載、內建 Modrinth 模組庫、即時玩家管理、圖形化屬性設定，以及無縫整合的 FRP 內網穿透互動介面，讓開服變得前所未有的簡單。

### 📸 面板預覽
[![Dashboard Screenshot](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image.png?raw=true)](https://github.com/jr4570/CraftNode-Server-Panel/blob/main/PNG/image.png?raw=true)

### ✨ 核心功能

* **🗂️ 多站點隔離管理**：建立多個獨立的伺服器資料夾，自由切換不同版本與生態系，檔案互不干擾。
* **⚙️ 一鍵核心部署**：內建抓取最新 Paper、Vanilla、Fabric 版本，一鍵下載並自動同意 EULA。
* **🛠️ 圖形化屬性設定**：拋棄繁瑣的文字檔！透過拉桿與選單輕鬆設定 RAM 大小、Aikar 最佳化參數、連接埠與遊戲機制（自動同步覆寫 `server.properties`）。
* **📦 內建 Modrinth 市集**：直接在面板內搜尋、下載並管理模組與插件，支援一鍵安裝、停用與刪除。
* **📟 即時控制台與硬體監控**：即時顯示伺服器日誌，並附帶 CPU、RAM、硬碟與網路的即時監控數據。
* **👥 玩家與權限管理**：智慧解析登入狀態，一鍵給予 OP、切換遊戲模式、踢出或封鎖玩家。
* **📅 地圖快照備份**：一鍵將世界地圖打包為 ZIP 備份，支援隨時安全還原，保護您的心血。
* **🌐 內網穿透 (FRP) 支援**：內建 FRP 互動介面，無需實體 IP 也能輕鬆讓朋友連線。
* **🌙 現代化 UI 與系統匣**：支援深色 / 淺色主題切換、中英雙語，並支援「安全關機」後縮小至系統匣於背景運作。

### 🚀 系統需求與安裝

**環境要求：**
* Python 3.8 或以上版本。
* 運行 Minecraft 伺服器所需的對應 Java 版本（例如 MC 1.20+ 需要 Java 17 或 21）。

**1. 取得程式碼：**
```bash
git clone [https://github.com/jr4570/CraftNode-Server-Panel.git](https://github.com/jr4570/CraftNode-Server-Panel.git)
cd CraftNode-Server-Panel
```

**2. 安裝依賴套件：**
```bash
pip install PySide6 requests psutil
```

**3. 啟動面板：**
```bash
python CraftNode.py
```
*(可選) 若要使用內網穿透功能，請自行下載 FRP 用戶端，並在面板中指定執行檔路徑。*

### 📦 打包為獨立執行檔 (EXE)

如果您希望將此面板打包為不需要安裝 Python 環境的 Windows 獨立執行檔 (`.exe`)，以便於分發或快速啟動，可以使用 **PyInstaller** 進行編譯：

1. **安裝 PyInstaller：**
   ```bash
   pip install pyinstaller
   ```

2. **執行打包指令：**
   在專案根目錄下執行以下指令：
   ```bash
   pyinstaller --noconsole --onefile --name="CraftNodePanel" CraftNode.py
   ```
   * **`--noconsole`**：隱藏後台的命令提示字元視窗，提供純粹的 GUI 圖形介面體驗。
   * **`--onefile`**：將所有依賴庫與程式碼封裝進單一一個 `.exe` 檔案中。
   * **`--name`**：指定輸出的執行檔名稱。

3. **取得執行檔：**
   打包完成後，您可以在專案目錄下新生成的 `dist/` 資料夾中找到 `CraftNodePanel.exe`。直接雙擊該執行檔即可獨立運作（首次執行同樣會自動建立 `servers/` 目錄與設定檔）。

### 📜 開源聲明

本專案為免費開源軟體，您可以自由修改原始碼以符合自身需求。**唯嚴禁將本軟體直接或變相作為私有商業專案進行販售獲利。**
