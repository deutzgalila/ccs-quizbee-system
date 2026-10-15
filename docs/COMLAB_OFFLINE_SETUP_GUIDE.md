# Computer Lab Quick Deployment & Configuration Runbook
**OLFU College of Computer Studies — IT Olympics Quiz Bee System (ITPM 311)**

---

## 1. Quick Answer: Can I Just Zip & Run `npm start` on Windows?

**Yes, with one essential technical rule:**
- **Why `node_modules` was excluded from this ZIP:** Node.js uses `better-sqlite3`, a high-performance native C++ library. On Linux, it compiles to an ELF shared library (`.so`). On Windows, it requires a Windows PE binary (`.node`/`.dll`).
- **How it's handled seamlessly for you:**
  1. The zipped bundle includes the complete project, web assets, test suites, sample question CSVs, pre-seeded SQLite database (`quizbee.db`), and automated batch scripts.
  2. The bundled `start-windows.bat` automatically verifies Node.js, runs `npm install` on first launch (taking ~5–10 seconds to fetch the pre-compiled Windows x64 binary), verifies `quizbee.db`, detects your local LAN IP addresses, and starts the server.
  3. If your lab PC is completely offline (air-gapped without internet), connect the host PC to mobile hotspot or campus Wi-Fi for just **30 seconds** while running `start-windows.bat` once to let npm install. After that initial download, the host PC can remain **100% offline indefinitely**.

---

## 2. Package Summary & Download

- **Deployable Archive Path:** `/home/javvii/YearIII/ITPM311/quizbee-comlab-deploy.zip`
- **File Size:** ~548 KB (clean, lightweight, portable)
- **Included in Package:**
  - `start-windows.bat`: 1-click launcher, dependency checker, IP autodetection, and self-healing native module repair.
  - `reset-database-windows.bat`: 1-click database & session reset utility (resets 60 terminals to 0 PTS, clears all submissions and cheat logs, reloads question bank).
  - `allow-firewall-windows.bat`: 1-click firewall configuration for Windows.
  - `quizbee.db`: Pre-seeded, ready-to-use SQLite database.
  - `sample_questions.csv` & `sample_trial_questions.csv`: Question banks.
  - `public/`: High-definition UI views (Contestant, Quizmaster, Stage Projector, Judge, Landing Hub).
  - `src/`: Authoritative game engine, WebSocket synchronization, and security telemetry.

---

## 3. Step-by-Step Computer Lab Host Setup (Windows)

### Step 1: Unzip Archive
Extract `quizbee-comlab-deploy.zip` to a clean folder on the host PC (e.g., `C:\quizbee` or `Desktop\quizbee`).

### Step 2: Open Inbound Firewall Port 3000
1. In the extracted folder, right-click `allow-firewall-windows.bat`.
2. Click **Run as administrator**.
3. A command prompt will confirm:
   ```text
   [SUCCESS] Firewall rule "OLFU QuizBee Server" created successfully!
   Port 3000 is now accessible to other computers on the lab network.
   ```

### Step 3: Launch Server
Double-click `start-windows.bat`. The launcher will:
1. Detect Node.js.
2. Install Windows dependencies if missing.
3. Check `quizbee.db`.
4. Detect and display the exact LAN IPv4 URLs to give to contestants and judges.
5. Boot the server on port `3000`.

---

## 4. LAN & Network Configuration in Campus Labs

### Scenario A: All PCs in Lab are Connected via Switch / Router (DHCP)
1. Verify the Host IP displayed by `start-windows.bat` (e.g. `http://192.168.1.50:3000/`).
2. On any contestant or judge workstation, open Chrome/Edge and navigate to `http://192.168.1.50:3000/`.

### Scenario B: Lab Network has "AP Isolation" or "Client Isolation"
Some campus lab switches or VLANs isolate individual client ports to prevent communication between student PCs.
- **Symptom:** Contestant PC cannot load `http://<HOST_IP>:3000/` or ping times out.
- **Remedy:**
  - Connect the Host PC, Quizmaster laptop, and Contestant PCs to a dedicated unmanaged Gigabit switch or a local wireless router/hotspot brought for the event.
  - Confirm connectivity by running on a client PC:
    ```cmd
    ping <HOST_IP>
    ```

### Scenario C: Static IP Configuration (When Lab has no DHCP Server)
If your lab uses static IPs without a router assigning addresses:
1. Press `Win + R`, type `ncpa.cpl`, press Enter.
2. Right-click Ethernet adapter $\rightarrow$ **Properties** $\rightarrow$ **Internet Protocol Version 4 (TCP/IPv4)**.
3. Configure:
   - **Host PC:**
     - IP Address: `192.168.1.100`
     - Subnet Mask: `255.255.255.0`
     - Gateway: `192.168.1.1` (or blank)
   - **Contestant PC 1:**
     - IP Address: `192.168.1.101`
     - Subnet Mask: `255.255.255.0`
   - **Contestant PC 2:**
     - IP Address: `192.168.1.102`
     - Subnet Mask: `255.255.255.0`
4. All client machines access the system at: `http://192.168.1.100:3000/`.

---

## 5. System Access URLs

| Interface | URL | Recommended Hardware |
| :--- | :--- | :--- |
| **Landing Hub** | `http://<HOST_IP>:3000/` | Any device / Bookmark |
| **Quizmaster Dashboard** | `http://<HOST_IP>:3000/quizmaster.html` | Quizmaster / Stage Host Laptop |
| **Contestant Terminal** | `http://<HOST_IP>:3000/contestant.html` | Student Lab Workstations |
| **Projector / Stage View** | `http://<HOST_IP>:3000/projector.html` | Main Stage Projector / LED Wall |
| **Judge Scoring Panel** | `http://<HOST_IP>:3000/judge.html` | Judge Tablets or Laptops |

---

## 6. Pre-Event Verification Checklist (15-Minute Dry Run)

- [ ] **Firewall**: `allow-firewall-windows.bat` ran as Admin with `[SUCCESS]`.
- [ ] **Host IP**: Noted the IP printed in `start-windows.bat`.
- [ ] **Client Ping**: Ran `ping <HOST_IP>` from at least one contestant workstation.
- [ ] **Fullscreen & Anti-Cheat**: Open contestant terminal on a lab PC, click Fullscreen. Verify that switching tabs or pressing Alt+Tab logs a yellow warning on Quizmaster dashboard.
- [ ] **Concealment**: Lock an answer on the contestant screen and verify no visual cue gives away the selected choice to neighbors.
- [ ] **Projector Hide**: Trigger countdown from Quizmaster and verify stage projector hides question text/options until timer runs.
- [ ] **Session Reconnection**: Close contestant browser window during a round, reopen, enter PIN, and confirm reconnection with score intact.
- [ ] **Reset / Fresh Database**: To wipe scores and start fresh before the competition, stop the server with `Ctrl+C` and run:
  ```cmd
  npm run seed
  ```
