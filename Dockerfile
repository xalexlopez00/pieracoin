# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o pieracoin ./cmd/pieracoin

# Final stage
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/pieracoin /pieracoin
EXPOSE 8080
CMD ["/pieracoin"]