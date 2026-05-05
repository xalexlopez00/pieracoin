# PieraCoin V1.0 - Enterprise Blockchain

PieraCoin is an enterprise-grade blockchain implementation with a three-tier security architecture designed for high availability on cloud platforms like Render.

## Quick Start

```bash
# 1. Build and run the server
go run cmd/pieracoin/main.go

# 2. In another terminal, run admin panel
python admin_panel.py

# 3. In another terminal, run user wallet
python user_wallet.py
```

## Architecture

### Three-Tier Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    PieraCoin Backend (Go)                   │
│  ┌───────────────────┬──────────────────────────────────┐   │
│  │  Public Routes    │  Protected Routes (Admin Only)   │   │
│  │  - /health        │  - /miner/start                  │   │
│  │  - /wallet/*      │  - /miner/stop                   │   │
│  │  - /transaction   │  - /mine                         │   │
│  │  - /chain         │  - /metrics                      │   │
│  └───────────────────┴──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↓                              ↓
  ┌──────────────────┐      ┌──────────────────────┐
  │  User Wallet     │      │   Admin Panel        │
  │  (user_wallet.py)│      │  (admin_panel.py)    │
  │                  │      │                      │
  │ No secrets       │      │ Contains API_KEY     │
  │ Public queries   │      │ Controls mining      │
  │ Send txs         │      │ System monitoring    │
  └──────────────────┘      └──────────────────────┘
```

## Features

- **Cloud Native Architecture**: Graceful shutdown, health checks, rate limiting
- **Advanced Consensus**: PoW with smooth difficulty adjustment, fee-based mempool
- **Military-Grade Security**: HD wallets, replay protection, multi-signature scripts
- **Rich API**: REST API, JSON-RPC 2.0, webhooks
- **Observability**: Structured logging, Prometheus metrics
- **Secure Deployment**: Distroless Docker image

## Quick Start

```bash
go mod tidy
go build ./cmd/pieracoin
./pieracoin
```

## API Endpoints

### Public Endpoints (No Authentication Required)

- `GET /health` - Server health check
- `GET /wallet/generate` - Generate new wallet with mnemonic
- `POST /transaction` - Submit a transaction
- `GET /chain` - View blockchain and block information

### Admin Endpoints (Requires X-Admin-Key Header)

Requires header: `X-Admin-Key: <ADMIN_SECRET>`

- `POST /miner/start` - Start the mining process
- `POST /miner/stop` - Stop the mining process
- `POST /mine` - Mine a single block
- `GET /metrics` - Prometheus metrics endpoint

### Example Admin Request

```bash
# Start miner (requires admin key)
curl -X POST http://localhost:8080/miner/start \
  -H "X-Admin-Key: your-secret-key-here"

# Public request (no auth needed)
curl http://localhost:8080/health
```

## Client Applications

### Admin Panel (admin_panel.py)

Secure admin interface with the master API key embedded.

**Features:**
- Start/Stop mining
- Monitor system health and metrics
- Mine individual blocks
- View blockchain state

**Run:**
```bash
set ADMIN_KEY=your-secret-key-here
python admin_panel.py
```

### User Wallet (user_wallet.py)

Public-facing wallet application for regular users.

**Features:**
- Generate new wallets
- Check balance
- Send transactions
- View blockchain explorer
- Server health status

**Run:**
```bash
python user_wallet.py
```

## Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Backend Server
set ADMIN_SECRET=your-super-secret-admin-key-12345
set PORT=8080

# Admin Panel
set ADMIN_KEY=your-super-secret-admin-key-12345
set SERVER_URL=http://localhost:8080

# User Wallet
set SERVER_URL=http://localhost:8080
```

See `.env.example` for a template.

## Building Executables with PyInstaller

## Deployment on Render

### Step 1: Push to Git Repository

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your Git repository
4. Select "Docker" as runtime
5. Leave build/start commands as default

### Step 3: Set Environment Variables

In Render dashboard, go to Environment section and add:

```
ADMIN_SECRET=<generate-a-random-secure-key>
PORT=<leave blank, Render sets automatically>
```

**Important:** Choose a strong, random ADMIN_SECRET!

```bash
# Generate a secure random key (Linux/Mac):
openssl rand -hex 32

# Or use this online tool: https://www.random.org/bytes/
```

### Step 4: Deploy

Click "Deploy" and wait for the service to start.

### Step 5: Use the Public URL

Your service will get a URL like: `https://pieracoin.onrender.com`

**For Admin:**
```bash
set ADMIN_KEY=<your-ADMIN_SECRET-from-Render>
set SERVER_URL=https://pieracoin.onrender.com
python admin_panel.py
```

**For Users:**
```bash
set SERVER_URL=https://pieracoin.onrender.com
python user_wallet.py
```

## Building Executables with PyInstaller

Convert Python scripts to standalone EXE files.

### Installation

```bash
pip install pyinstaller
```

### Quick Build

Use the provided build script:

```bash
build_apps.bat
```

This creates:
- `dist/PieraCoin-Admin.exe` - Admin panel
- `dist/PieraCoin-Wallet.exe` - User wallet

### Manual Build

**Admin Panel (single file):**
```bash
pyinstaller --onefile --name "PieraCoin-Admin" admin_panel.py
```

**User Wallet:**
```bash
pyinstaller --onefile --name "PieraCoin-Wallet" user_wallet.py
```

### Distribution

1. **For Admin:** Distribute `PieraCoin-Admin.exe` with instructions to set `ADMIN_KEY` env var
2. **For Users:** Distribute `PieraCoin-Wallet.exe` (no secrets needed)

See `CLIENT_APPS.md` for detailed instructions.

## Keeping Render Service Alive

Render free tier services sleep after 15 minutes of inactivity.

### Recommended: UptimeRobot

1. Sign up at [UptimeRobot](https://uptimerobot.com) (free)
2. Create a monitor for: `https://pieracoin.onrender.com/health`
3. Set interval to 5 minutes
4. Service stays awake indefinitely!

## Testing

```bash
go test ./test/...
```

## Docker

```bash
docker build -t pieracoin .
docker run -p 8080:8080 pieracoin
```

## Support

For detailed information about client applications and PyInstaller, see:
- [CLIENT_APPS.md](CLIENT_APPS.md) - Complete guide for admin/user apps and EXE building
- [.env.example](.env.example) - Environment configuration template