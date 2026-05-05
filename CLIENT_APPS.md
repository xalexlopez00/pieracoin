# PieraCoin Security & Client Applications

## Architecture Overview

PieraCoin implements a three-tier security model:

### 1. **Backend Server (Go)** 
- Acts as the "bouncer" validating all requests
- Public routes: wallet generation, transaction submission, blockchain viewing
- Protected routes: miner control, metrics - require `X-Admin-Key` header

### 2. **Admin Panel (Python)**
- Includes the master API key
- Controls mining, system monitoring
- Only for administrators

### 3. **User Wallet (Python)**
- No admin credentials included
- Public operations only
- For regular users

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests`: HTTP client library
- `colorama`: Colored terminal output

### Step 2: Configure Environment Variables

#### For Admin Panel
```bash
# Set the admin secret key
set ADMIN_KEY=your-super-secret-admin-key-12345

# Set server URL (optional, defaults to http://localhost:8080)
set SERVER_URL=http://localhost:8080
```

#### For User Wallet
```bash
# Set server URL (optional, defaults to http://localhost:8080)
set SERVER_URL=http://localhost:8080
```

#### For Backend Server
```bash
# Set the admin secret (must match the client's ADMIN_KEY)
set ADMIN_SECRET=your-super-secret-admin-key-12345

# Set port (optional, defaults to 8080)
set PORT=8080
```

### Step 3: Run Applications

#### Start Backend Server
```bash
go run cmd/pieracoin/main.go
```

#### Run Admin Panel
```bash
python admin_panel.py
```

#### Run User Wallet
```bash
python user_wallet.py
```

---

## Packaging to EXE with PyInstaller

### Installation

```bash
pip install pyinstaller
```

### Building Admin Panel EXE (Single File - Recommended)

```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PieraCoin-Admin" ^
  --icon=icon.ico ^
  --add-data ".:." ^
  admin_panel.py
```

**Flags explained:**
- `--onefile`: Creates a single .exe file (not a folder)
- `--windowed`: No console window (remove for debugging)
- `--name`: Output executable name
- `--icon`: Application icon (optional)
- `--add-data`: Include data files if needed

**Output:** `dist/PieraCoin-Admin.exe`

### Building User Wallet EXE

```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PieraCoin-Wallet" ^
  --icon=icon.ico ^
  user_wallet.py
```

**Output:** `dist/PieraCoin-Wallet.exe`

### Optional: Create Icons

Generate a simple icon (256x256 PNG):
```bash
# Convert PNG to ICO (requires PIL)
pip install pillow

# Then convert:
python -c "from PIL import Image; Image.open('icon.png').convert('RGBA').save('icon.ico')"
```

Or use online tools like [icoconvert.com](https://icoconvert.com/)

---

## Distribution

### For Admin (Packaged)

1. **Build**: `pyinstaller --onefile admin_panel.py`
2. **Distribute**: Give them `dist/PieraCoin-Admin.exe`
3. **They set environment variable before running:**
   ```bash
   set ADMIN_KEY=their-secret-key
   PieraCoin-Admin.exe
   ```

### For Users (Packaged)

1. **Build**: `pyinstaller --onefile user_wallet.py`
2. **Distribute**: Give them `dist/PieraCoin-Wallet.exe`
3. **No secrets needed, they just run it!**
   ```bash
   set SERVER_URL=https://pieracoin.onrender.com
   PieraCoin-Wallet.exe
   ```

---

## Complete PyInstaller Build Script

Create `build_all.bat`:

```batch
@echo off
echo Building PieraCoin Applications...
echo.

echo [1/2] Building Admin Panel...
pyinstaller ^
  --onefile ^
  --name "PieraCoin-Admin" ^
  --add-data ".:." ^
  admin_panel.py

echo.
echo [2/2] Building User Wallet...
pyinstaller ^
  --onefile ^
  --name "PieraCoin-Wallet" ^
  user_wallet.py

echo.
echo Build complete! Check 'dist' folder for executables.
pause
```

Run with:
```bash
build_all.bat
```

---

## Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
pip install --no-cache-dir -r requirements.txt

# Rebuild with more verbose logging
pyinstaller --debug=imports admin_panel.py
```

### EXE won't start
- Check if server URL is correct: `set SERVER_URL=http://your-server:8080`
- Ensure environment variables are set BEFORE running .exe
- Run from Command Prompt, not PowerShell (sometimes has encoding issues)

### Antivirus warnings
PyInstaller sometimes triggers false positives. This is normal. If distributing commercially, consider code signing.

---

## Security Best Practices

1. **Never commit ADMIN_KEY to git**
   - Use environment variables only
   - Use `.env` files locally (add to .gitignore)

2. **Use HTTPS in production**
   - Set `SERVER_URL=https://your-domain.com`
   - Render provides free HTTPS

3. **Rotate admin keys regularly**
   - Set `ADMIN_SECRET` in Render environment variables
   - Change it periodically

4. **Keep Python dependencies updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Example Setup for Render

### Environment Variables in Render Dashboard

```
ADMIN_SECRET=super-secret-key-12345
PORT=8080
```

### User runs locally:
```bash
set SERVER_URL=https://your-pieracoin.onrender.com
python user_wallet.py
```

### Admin runs locally:
```bash
set ADMIN_KEY=super-secret-key-12345
set SERVER_URL=https://your-pieracoin.onrender.com
python admin_panel.py
```

---

## API Endpoints Reference

### Public Endpoints (No authentication)

- `GET /health` - Server health check
- `GET /wallet/generate` - Generate new wallet
- `GET /chain` - View blockchain
- `POST /transaction` - Submit transaction

### Admin Endpoints (Requires `X-Admin-Key` header)

- `POST /miner/start` - Start mining
- `POST /miner/stop` - Stop mining
- `POST /mine` - Mine single block
- `GET /metrics` - Prometheus metrics

---

## Support

For issues or questions:
1. Check server logs: `go run cmd/pieracoin/main.go`
2. Test connectivity: `curl http://localhost:8080/health`
3. Verify admin key: Check environment variable is set correctly
