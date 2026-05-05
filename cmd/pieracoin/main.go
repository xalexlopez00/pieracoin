package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"pieracoin/internal/blockchain"
	"pieracoin/internal/consensus"
	"pieracoin/internal/logging"
	"pieracoin/internal/metrics"
	"pieracoin/internal/network"
	"pieracoin/internal/security"
	"pieracoin/internal/wallet"
)

func main() {
	logger := logging.NewLogger()

	// Initialize components
	bc := blockchain.NewBlockchain(logger)
	cons := consensus.NewConsensus(bc, logger)
	wal := wallet.NewWallet(logger)
	sec := security.NewSecurity(logger)
	met := metrics.NewMetrics(logger)
	net := network.NewNetwork(bc, cons, wal, sec, met, logger)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	srv := &http.Server{
		Addr:    ":" + port,
		Handler: net.Router(),
	}

	// Graceful shutdown
	go func() {
		logger.Info().Str("port", port).Msg("Starting PieraCoin node")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal().Err(err).Msg("Server failed to start")
		}
	}()

	// Auto-ping to keep internal process alive (Note: This doesn't prevent Render shutdown)
	go func() {
		ticker := time.NewTicker(10 * time.Minute)
		defer ticker.Stop()
		client := &http.Client{Timeout: 5 * time.Second}
		for {
			select {
			case <-ticker.C:
				resp, err := client.Get("http://localhost:" + port + "/health")
				if err != nil {
					logger.Warn().Err(err).Msg("Auto-ping failed")
				} else {
					resp.Body.Close()
					logger.Debug().Msg("Auto-ping successful")
				}
			}
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logger.Info().Msg("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal().Err(err).Msg("Server forced to shutdown")
	}

	// Close databases safely
	bc.Close()
	logger.Info().Msg("Server exited")
}
