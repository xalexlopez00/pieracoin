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
	srv := &http.Server{
		Addr:    ":8080",
		Handler: net.Router(),
	}

	// Graceful shutdown
	go func() {
		logger.Info().Msg("Starting PieraCoin node on :8080")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal().Err(err).Msg("Server failed to start")
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