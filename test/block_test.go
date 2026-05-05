package test

import (
	"encoding/json"
	"testing"
	"time"

	"pieracoin/internal/blockchain"
	"pieracoin/internal/logging"
	"pieracoin/pkg/crypto"
)

func TestBlockHash(t *testing.T) {
	logger := logging.NewLogger()
	bc := blockchain.NewBlockchain(logger)

	block := blockchain.Block{
		Index:        1,
		Timestamp:    time.Now(),
		Transactions: []blockchain.Transaction{},
		PrevHash:     bc.GetLatestBlock().Hash,
		Hash:         "",
		Nonce:        0,
		Difficulty:   1,
	}

	// Calculate hash
	hash := calculateHash(block)
	if hash == "" {
		t.Error("Hash should not be empty")
	}

	// Verify hash is consistent
	hash2 := calculateHash(block)
	if hash != hash2 {
		t.Error("Hash should be consistent")
	}
}

func calculateHash(block blockchain.Block) string {
	data, _ := json.Marshal(block)
	return crypto.ToHex(crypto.HashDoubleSHA256(data))
}