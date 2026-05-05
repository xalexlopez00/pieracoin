package network

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/rs/zerolog"
	"golang.org/x/time/rate"
	"pieracoin/internal/blockchain"
	"pieracoin/internal/consensus"
	"pieracoin/internal/metrics"
	"pieracoin/internal/security"
	"pieracoin/internal/wallet"
)

type Network struct {
	blockchain *blockchain.Blockchain
	consensus  *consensus.Consensus
	wallet     *wallet.Wallet
	security   *security.Security
	metrics    *metrics.Metrics
	logger     zerolog.Logger
	limiter    *rate.Limiter
}

func NewNetwork(bc *blockchain.Blockchain, cons *consensus.Consensus, wal *wallet.Wallet, sec *security.Security, met *metrics.Metrics, logger zerolog.Logger) *Network {
	return &Network{
		blockchain: bc,
		consensus:  cons,
		wallet:     wal,
		security:   sec,
		metrics:    met,
		logger:     logger,
		limiter:    rate.NewLimiter(rate.Every(time.Second), 10), // 10 requests per second
	}
}

func (n *Network) Router() *mux.Router {
	r := mux.NewRouter()

	// Rate limiting middleware
	r.Use(n.rateLimitMiddleware)

	// API routes
	r.HandleFunc("/health", n.healthCheck).Methods("GET")
	r.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		n.metrics.Handler().ServeHTTP(w, r)
	}).Methods("GET")
	r.HandleFunc("/mine", n.mineBlock).Methods("POST")
	r.HandleFunc("/transaction", n.submitTransaction).Methods("POST")
	r.HandleFunc("/wallet/generate", n.generateWallet).Methods("GET")

	// JSON-RPC
	r.HandleFunc("/jsonrpc", n.jsonRPC).Methods("POST")

	return r
}

func (n *Network) rateLimitMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !n.limiter.Allow() {
			http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func (n *Network) healthCheck(w http.ResponseWriter, r *http.Request) {
	// Check database accessibility (simplified)
	if len(n.blockchain.Blocks) == 0 {
		http.Error(w, "Database not accessible", http.StatusServiceUnavailable)
		return
	}
	// Check sync status (simplified)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

func (n *Network) mineBlock(w http.ResponseWriter, r *http.Request) {
	block := n.consensus.MineBlock()
	n.blockchain.AddBlock(*block)
	json.NewEncoder(w).Encode(block)
}

func (n *Network) submitTransaction(w http.ResponseWriter, r *http.Request) {
	var tx blockchain.Transaction
	json.NewDecoder(r.Body).Decode(&tx)
	n.consensus.AddToMempool(&tx)
	json.NewEncoder(w).Encode(map[string]string{"status": "added"})
}

func (n *Network) generateWallet(w http.ResponseWriter, r *http.Request) {
	mnemonic, _ := n.wallet.GenerateMnemonic()
	json.NewEncoder(w).Encode(map[string]string{"mnemonic": mnemonic})
}

func (n *Network) jsonRPC(w http.ResponseWriter, r *http.Request) {
	var req map[string]interface{}
	json.NewDecoder(r.Body).Decode(&req)
	// Simplified JSON-RPC handling
	response := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      req["id"],
		"result":  "method not implemented",
	}
	json.NewEncoder(w).Encode(response)
}

// Webhooks would be implemented here, e.g., notify on transaction to address