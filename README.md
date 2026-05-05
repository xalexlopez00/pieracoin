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