# PieraCoin V1.0 Release

## 🚀 Quick Start

### No installation required! Just run the executables:

```
release/
├── start-server.bat          → Start the blockchain node
├── start-admin-panel.bat     → Start admin control panel
├── start-user-wallet.bat     → Start user wallet app
│
├── pieracoin.exe             → Backend server (run manually)
├── PieraCoin-Admin.exe       → Admin GUI (run manually)
└── PieraCoin-Wallet.exe      → User wallet GUI (run manually)
```

### Option 1: Run batch scripts (easiest)

1. **Start the server:**
   ```bash
   cd release/
   start-server.bat
   ```

2. **Start admin panel (in another window):**
   ```bash
   cd release/
   start-admin-panel.bat
   ```

3. **Start user wallet (in another window):**
   ```bash
   cd release/
   start-user-wallet.bat
   ```

### Option 2: Run EXEs directly

```bash
cd release/

# Terminal 1: Start server
pieracoin.exe

# Terminal 2: Start admin panel (requires ADMIN_KEY environment variable)
PieraCoin-Admin.exe

# Terminal 3: Start user wallet
PieraCoin-Wallet.exe
```

## 🔑 Configuration

### For Admin Panel
Set the admin secret key before running:

**Windows (PowerShell):**
```powershell
$env:ADMIN_KEY = "your-super-secret-key-here"
$env:SERVER_URL = "http://localhost:8080"  # or your server URL
.\PieraCoin-Admin.exe
```

**Windows (CMD):**
```cmd
set ADMIN_KEY=your-super-secret-key-here
set SERVER_URL=http://localhost:8080
PieraCoin-Admin.exe
```

### Default Configuration

If no environment variables are set, the apps use:

- **Server URL:** `https://pieracoin.onrender.com` (public Render deployment)
- **Admin Key:** `P@ssw0rd_1` (default - CHANGE IN PRODUCTION)
- **Port:** `8080` (for local server)

## 📋 Features

### 🖥️ PieraCoin Node Server (pieracoin.exe)

- REST API with JSON responses
- Blockchain consensus (PoW)
- Wallet generation and address derivation
- Real-time metrics (Prometheus format)
- Graceful shutdown handling
- Cloud-native deployment ready

**Endpoints:**
- Public: `/health`, `/wallet/generate`, `/chain`, `/transactions`, `/balance/{addr}`, `/mine`
- Admin: `/miner/start`, `/miner/stop`, `/metrics`, `/mint`

### 👨‍💼 Admin Panel (PieraCoin-Admin.exe)

- **Dark mode GUI** with customtkinter
- Real-time blockchain dashboard
- Mining control (start/stop global mining)
- Local mining with progress tracking (45 seconds)
- Wallet address management
- Admin coin injection (minting)
- Threading for non-blocking UI

**Login:**
1. Enter your ADMIN_KEY
2. Optionally change Server URL
3. Click "Connect"

**Tabs:**
- **Dashboard:** Real-time blockchain status
- **Mining:** Mine blocks locally with reward address
- **Wallets:** View all generated addresses (admin-only)
- **Mint:** Inject coins into any address (admin-only)

### 👤 User Wallet (PieraCoin-Wallet.exe)

- **Dark mode GUI** with customtkinter  
- Generate wallets with secure seed phrases
- Mining with visual progress (45 seconds)
- Check address balances
- View transaction history
- Server health monitoring
- Dynamic server URL configuration

**Tabs:**
- **Wallet:** Generate new wallet and view mnemonic
- **Mining:** Mine blocks and earn rewards
- **Balance:** Query any address balance
- **History:** View all blockchain transactions

## 🔐 Security Notes

1. **Admin Key:** Change the default admin key before production use
2. **Seed Phrases:** Store seed phrases securely - they're your wallet!
3. **Private Keys:** Never share your private keys or seed phrases
4. **Environment Variables:** Don't hardcode secrets in scripts

## 🛠️ Troubleshooting

### "Cannot connect to server"
- Ensure the blockchain node is running
- Check that the SERVER_URL is correct
- Verify firewall isn't blocking port 8080 (local) or 443 (Render)

### Admin panel won't start
- Verify ADMIN_KEY environment variable is set
- Check that you're using the correct key
- Ensure server is running and accessible

### GUI appears but buttons don't work
- Check that SERVER_URL is accessible
- Look at server logs for error responses
- Verify network connectivity

### Mining seems slow
- Mining intentionally takes 45 seconds
- This simulates real PoW work
- It's normal - just wait for completion

## 📦 What's Included

```
release/
├── pieracoin.exe              (8.5 MB) - Blockchain node
├── PieraCoin-Admin.exe        (30 MB)  - Admin GUI with all dependencies
├── PieraCoin-Wallet.exe       (30 MB)  - User wallet GUI with all dependencies
├── start-server.bat           - Server launcher
├── start-admin-panel.bat      - Admin GUI launcher
└── start-user-wallet.bat      - Wallet launcher
```

**Total size:** ~68.5 MB (all standalone, no external dependencies)

## 🔄 Rebuilding from Source

### For Go Backend (recommended - simple!):

```powershell
cd <project-root>
go build -o pieracoin.exe ./cmd/pieracoin
Copy-Item pieracoin.exe release/
```

### For Python GUIs (requires Python 3.8+):

> **Note:** The included Python EXEs in `release/` are fully functional and standalone. 
> Only rebuild if you've modified the Python source code or need the latest version.

**Prerequisites:**
1. Install Python 3.8+ (https://python.org)
2. Install dependencies: `pip install -r requirements.txt`
3. Install PyInstaller: `pip install pyinstaller`

**Build:**

```powershell
# Navigate to project root
cd <project-root>

# Build Admin Panel
pyinstaller PieraCoin-Admin.spec
Copy-Item dist/PieraCoin-Admin.exe release/ -Force

# Build User Wallet
pyinstaller PieraCoin-Wallet.spec
Copy-Item dist/PieraCoin-Wallet.exe release/ -Force
```

**Build Details:**
- Each EXE is ~30 MB (all dependencies bundled)
- Build takes 2-3 minutes per app
- No additional Python installation needed on target machine
- Uses UPX compression for smaller size (optional)

### Complete Build Script (PowerShell):

```powershell
# Build all executables
$ErrorActionPreference = "Stop"

Write-Host "Building PieraCoin Release..." -ForegroundColor Cyan

# Go Backend
Write-Host "Building Go backend..." -ForegroundColor Yellow
go build -o pieracoin.exe ./cmd/pieracoin
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Backend built" -ForegroundColor Green }

# Python Apps (requires Python installed)
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Building Python apps..." -ForegroundColor Yellow
    
    python -m pip install -q pyinstaller
    
    pyinstaller PieraCoin-Admin.spec
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ Admin app built" -ForegroundColor Green }
    
    pyinstaller PieraCoin-Wallet.spec
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ Wallet app built" -ForegroundColor Green }
    
    # Copy to release
    Copy-Item pieracoin.exe release/ -Force
    Copy-Item dist/*.exe release/ -Force
    Write-Host "✓ All binaries copied to release/" -ForegroundColor Green
} else {
    Write-Host "⚠ Python not found - skipping GUI builds" -ForegroundColor Yellow
    Write-Host "  To build GUIs: pip install pyinstaller, then pyinstaller *.spec" -ForegroundColor Gray
    
    # Copy Go backend only
    Copy-Item pieracoin.exe release/ -Force
    Write-Host "✓ Backend copied to release/" -ForegroundColor Green
}

Write-Host "Build complete!" -ForegroundColor Cyan
```

## 📊 Deployment on Render

The server is configured for Render.com deployment:

1. Set environment variables in Render dashboard:
   - `ADMIN_SECRET` - your admin key
   - `PORT` - automatically set by Render (3000-10000)

2. The app will:
   - Listen on the PORT environment variable
   - Send periodic pings to keep the service warm
   - Gracefully handle shutdown signals

3. Public URL will be: `https://pieracoin.onrender.com`

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs in `pieracoin` console
3. Check the GitHub repository for updates

## 📜 License

PieraCoin V1.0 - Enterprise Blockchain Platform
