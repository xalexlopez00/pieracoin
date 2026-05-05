# PieraCoin V1.0

PieraCoin is an enterprise-grade blockchain implementation designed for high availability on cloud platforms like Render.

## Features

- **Cloud Native Architecture**: Graceful shutdown, health checks, rate limiting
- **Advanced Consensus**: PoW with smooth difficulty adjustment, fee-based mempool
- **Military-Grade Security**: HD wallets, replay protection, multi-signature scripts
- **Rich API**: REST API, JSON-RPC 2.0, webhooks
- **Observability**: Structured logging, Prometheus metrics
- **Secure Deployment**: Distroless Docker image

## Building

```bash
go mod tidy
go build ./cmd/pieracoin
```

## Running

```bash
./pieracoin
```

## Testing

```bash
go test ./test/...
```

## Docker

```bash
docker build -t pieracoin .
docker run -p 8080:8080 pieracoin
```