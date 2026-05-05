package blockchain

import (
	"encoding/json"
	"sync"
	"time"

	"github.com/rs/zerolog"
	"pieracoin/pkg/crypto"
)

type Transaction struct {
	ID        string    `json:"id"`
	From      string    `json:"from"`
	To        string    `json:"to"`
	Amount    float64   `json:"amount"`
	Fee       float64   `json:"fee"`
	Timestamp time.Time `json:"timestamp"`
	Nonce     uint64    `json:"nonce"`
	Signature string    `json:"signature"`
}

type Block struct {
	Index        int           `json:"index"`
	Timestamp    time.Time     `json:"timestamp"`
	Transactions []Transaction `json:"transactions"`
	PrevHash     string        `json:"prev_hash"`
	Hash         string        `json:"hash"`
	Nonce        uint64        `json:"nonce"`
	Difficulty   uint32        `json:"difficulty"`
}

type Blockchain struct {
	Blocks []Block
	mu     sync.RWMutex
	logger zerolog.Logger
}

func NewBlockchain(logger zerolog.Logger) *Blockchain {
	genesis := Block{
		Index:        0,
		Timestamp:    time.Now(),
		Transactions: []Transaction{},
		PrevHash:     "",
		Hash:         "",
		Nonce:        0,
		Difficulty:   1,
	}
	genesis.Hash = calculateHash(genesis)
	return &Blockchain{
		Blocks: []Block{genesis},
		logger: logger,
	}
}

func (bc *Blockchain) AddBlock(block Block) {
	bc.mu.Lock()
	defer bc.mu.Unlock()
	bc.Blocks = append(bc.Blocks, block)
	bc.logger.Info().Int("index", block.Index).Msg("Block added to blockchain")
}

func (bc *Blockchain) GetLatestBlock() Block {
	bc.mu.RLock()
	defer bc.mu.RUnlock()
	return bc.Blocks[len(bc.Blocks)-1]
}

func (bc *Blockchain) Close() {
	// Simulate closing databases
	bc.logger.Info().Msg("Blockchain database closed safely")
}

func calculateHash(block Block) string {
	data, _ := json.Marshal(block)
	return crypto.ToHex(crypto.HashDoubleSHA256(data))
}