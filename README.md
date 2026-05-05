# PieraCoin V1.0

PieraCoin is an enterprise-grade blockchain implementation designed for high availability on cloud platforms like Render.

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

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /mine` - Mine a new block
- `POST /transaction` - Submit transaction
- `GET /wallet/generate` - Generate new wallet

## Keeping Render Service Alive

Render free tier services sleep after 15 minutes of inactivity. To prevent this:

### Option 1: External Uptime Monitor (Recommended)
1. Sign up for [UptimeRobot](https://uptimerobot.com) (free tier available)
2. Add your Render URL (e.g., `https://pieracoin.onrender.com/health`)
3. Set monitoring interval to 5 minutes
4. UptimeRobot will send pings automatically

### Option 2: Cron Job Service
Use [cron-job.org](https://cron-job.org) or similar:
- URL: `https://your-render-url.onrender.com/health`
- Schedule: Every 10 minutes
- Method: GET

### Option 3: Browser Automation
Keep a browser tab open with a simple HTML page that refreshes every 10 minutes:

```html
<!DOCTYPE html>
<html>
<head>
    <title>PieraCoin Keep Alive</title>
    <script>
        setInterval(() => {
            fetch('https://your-render-url.onrender.com/health')
                .then(response => console.log('Ping sent'))
                .catch(error => console.log('Ping failed'));
        }, 600000); // 10 minutes
    </script>
</head>
<body>
    <h1>PieraCoin is alive!</h1>
</body>
</html>
```

### Internal Auto-Ping
The application includes an internal auto-ping mechanism that pings `/health` every 10 minutes to keep the process active. However, **this does not prevent Render from shutting down the service** - Render requires external HTTP traffic.

## Deployment on Render

1. **Push to Git Repository**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your Git repository
   - Select "Docker" as runtime
   - Set build command: (leave default)
   - Set start command: (leave default, uses Dockerfile CMD)

3. **Environment Variables**
   - Render automatically sets `PORT`
   - No additional env vars needed

4. **Health Check**
   - Set health check path: `/health`
   - Render will monitor the endpoint

## Testing

```bash
go test ./test/...
```

## Docker

```bash
docker build -t pieracoin .
docker run -p 8080:8080 pieracoin
```