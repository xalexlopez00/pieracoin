package network

import (
	"encoding/json"
	"net/http"
	"os"
	"time"

	"pieracoin/internal/blockchain"
	"pieracoin/internal/consensus"
	"pieracoin/internal/metrics"
	"pieracoin/internal/security"
	"pieracoin/internal/wallet"

	"github.com/gorilla/mux"
	"github.com/rs/zerolog"
	"golang.org/x/time/rate"
)

type Network struct {
	blockchain     *blockchain.Blockchain
	consensus      *consensus.Consensus
	wallet         *wallet.Wallet
	security       *security.Security
	metrics        *metrics.Metrics
	logger         zerolog.Logger
	limiter        *rate.Limiter
	miningPaused   bool
	generatedAddrs []string
}

func NewNetwork(bc *blockchain.Blockchain, cons *consensus.Consensus, wal *wallet.Wallet, sec *security.Security, met *metrics.Metrics, logger zerolog.Logger) *Network {
	return &Network{
		blockchain:   bc,
		consensus:    cons,
		wallet:       wal,
		security:     sec,
		metrics:      met,
		logger:       logger,
		limiter:      rate.NewLimiter(rate.Every(time.Second), 10), // 10 requests per second
		miningPaused: false,
	}
}

func (n *Network) Router() *mux.Router {
	r := mux.NewRouter()

	// Rate limiting middleware
	r.Use(n.rateLimitMiddleware)

	// Public API routes
	r.HandleFunc("/health", n.healthCheck).Methods("GET")
	r.HandleFunc("/wallet/generate", n.generateWallet).Methods("GET")
	r.HandleFunc("/transaction", n.submitTransaction).Methods("POST")
	r.HandleFunc("/balance/{address}", n.getBalance).Methods("GET")
	r.HandleFunc("/chain", n.getChain).Methods("GET")
	r.HandleFunc("/transactions", n.getTransactions).Methods("GET")
	r.HandleFunc("/mine", n.mineBlock).Methods("POST")

	// Protected (Admin Only) routes
	r.HandleFunc("/miner/start", n.adminRequired(n.startMiner)).Methods("POST")
	r.HandleFunc("/miner/stop", n.adminRequired(n.stopMiner)).Methods("POST")
	r.HandleFunc("/wallets", n.adminRequired(n.getWallets)).Methods("GET")
	r.HandleFunc("/mint", n.adminRequired(n.mintCoins)).Methods("POST")
	r.HandleFunc("/metrics", n.adminRequired(n.getMetrics)).Methods("GET")

	// JSON-RPC (Public)
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

// adminRequired middleware validates the X-Admin-Key header
func (n *Network) adminRequired(handler http.HandlerFunc) http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		adminSecret := os.Getenv("ADMIN_SECRET")
		if adminSecret == "" {
			n.logger.Warn().Msg("ADMIN_SECRET not set")
			http.Error(w, "Server not configured", http.StatusInternalServerError)
			return
		}

		adminKey := r.Header.Get("X-Admin-Key")
		if adminKey != adminSecret {
			n.logger.Warn().Str("ip", r.RemoteAddr).Msg("Unauthorized admin access attempt")
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		handler(w, r)
	})
}

func (n *Network) healthCheck(w http.ResponseWriter, r *http.Request) {
	if len(n.blockchain.Blocks) == 0 {
		http.Error(w, "Database not accessible", http.StatusServiceUnavailable)
		return
	}
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":        "healthy",
		"blocks":        len(n.blockchain.Blocks),
		"mining_paused": n.miningPaused,
	})
}

func (n *Network) mineBlock(w http.ResponseWriter, r *http.Request) {
	if n.miningPaused {
		http.Error(w, "Mining is currently paused by admin", http.StatusServiceUnavailable)
		return
	}

	var body struct {
		MinerAddress string `json:"miner_address"`
	}
	json.NewDecoder(r.Body).Decode(&body)

	block := n.consensus.MineBlock(body.MinerAddress)
	n.blockchain.AddBlock(*block)
	json.NewEncoder(w).Encode(block)
}

func (n *Network) submitTransaction(w http.ResponseWriter, r *http.Request) {
	var tx blockchain.Transaction
	if err := json.NewDecoder(r.Body).Decode(&tx); err != nil {
		http.Error(w, "Invalid transaction payload", http.StatusBadRequest)
		return
	}
	n.consensus.AddToMempool(&tx)
	json.NewEncoder(w).Encode(map[string]string{"status": "added"})
}

func (n *Network) generateWallet(w http.ResponseWriter, r *http.Request) {
	mnemonic, err := n.wallet.GenerateMnemonic()
	if err != nil {
		http.Error(w, "Cannot generate wallet", http.StatusInternalServerError)
		return
	}
	address, err := n.wallet.AddressFromMnemonic(mnemonic)
	if err != nil {
		http.Error(w, "Cannot derive address", http.StatusInternalServerError)
		return
	}
	n.generatedAddrs = append(n.generatedAddrs, address)
	json.NewEncoder(w).Encode(map[string]string{
		"mnemonic": mnemonic,
		"address":  address,
	})
}

func (n *Network) getBalance(w http.ResponseWriter, r *http.Request) {
	address := mux.Vars(r)["address"]
	balance := 0.0
	for _, block := range n.blockchain.Blocks {
		for _, tx := range block.Transactions {
			if tx.To == address {
				balance += tx.Amount
			}
			if tx.From == address {
				balance -= tx.Amount + tx.Fee
			}
		}
	}
	json.NewEncoder(w).Encode(map[string]interface{}{
		"address": address,
		"balance": balance,
	})
}

func (n *Network) getChain(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]interface{}{
		"blocks": len(n.blockchain.Blocks),
		"chain":  n.blockchain.Blocks,
	})
}

func (n *Network) getTransactions(w http.ResponseWriter, r *http.Request) {
	transactions := []blockchain.Transaction{}
	for _, block := range n.blockchain.Blocks {
		transactions = append(transactions, block.Transactions...)
	}
	json.NewEncoder(w).Encode(map[string]interface{}{
		"count":        len(transactions),
		"transactions": transactions,
	})
}

func (n *Network) getWallets(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]interface{}{
		"wallets": n.generatedAddrs,
	})
}

func (n *Network) mintCoins(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Address string  `json:"address"`
		Amount  float64 `json:"amount"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, "Invalid mint payload", http.StatusBadRequest)
		return
	}
	if body.Address == "" || body.Amount <= 0 {
		http.Error(w, "Address and amount required", http.StatusBadRequest)
		return
	}
	transaction := blockchain.Transaction{
		ID:        "mint-" + body.Address + "-" + time.Now().Format(time.RFC3339Nano),
		From:      "MINT",
		To:        body.Address,
		Amount:    body.Amount,
		Fee:       0,
		Timestamp: time.Now(),
		Nonce:     uint64(time.Now().UnixNano()),
	}
	n.consensus.AddToMempool(&transaction)
	block := n.consensus.MineBlock("")
	n.blockchain.AddBlock(*block)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "minted",
		"block":  block,
	})
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

// Admin-only handlers

func (n *Network) startMiner(w http.ResponseWriter, r *http.Request) {
	n.miningPaused = false
	n.logger.Info().Msg("Miner started by admin")
	json.NewEncoder(w).Encode(map[string]string{
		"status":    "Miner started",
		"timestamp": time.Now().String(),
	})
}

func (n *Network) stopMiner(w http.ResponseWriter, r *http.Request) {
	n.miningPaused = true
	n.logger.Info().Msg("Miner stopped by admin")
	json.NewEncoder(w).Encode(map[string]string{
		"status":    "Miner stopped",
		"timestamp": time.Now().String(),
	})
}

func (n *Network) getMetrics(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain")
	n.metrics.Handler().ServeHTTP(w, r)
}

// Webhooks would be implemented here, e.g., notify on transaction to address
