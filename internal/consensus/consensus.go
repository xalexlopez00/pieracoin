package consensus

import (
	"encoding/json"
	"math/bits"
	"sort"
	"time"

	"pieracoin/internal/blockchain"
	"pieracoin/pkg/crypto"

	"github.com/rs/zerolog"
)

type Mempool struct {
	txs []*blockchain.Transaction
}

func (m *Mempool) Push(tx *blockchain.Transaction) {
	m.txs = append(m.txs, tx)
	sort.Slice(m.txs, func(i, j int) bool {
		return m.txs[i].Fee > m.txs[j].Fee // Higher fee first
	})
}

func (m *Mempool) Pop() *blockchain.Transaction {
	if len(m.txs) == 0 {
		return nil
	}
	tx := m.txs[0]
	m.txs = m.txs[1:]
	return tx
}

type Consensus struct {
	blockchain *blockchain.Blockchain
	mempool    *Mempool
	logger     zerolog.Logger
}

func NewConsensus(bc *blockchain.Blockchain, logger zerolog.Logger) *Consensus {
	return &Consensus{
		blockchain: bc,
		mempool:    &Mempool{},
		logger:     logger,
	}
}

func (c *Consensus) MineBlock(minerAddress string) *blockchain.Block {
	latest := c.blockchain.GetLatestBlock()
	newBlock := blockchain.Block{
		Index:        latest.Index + 1,
		Timestamp:    time.Now(),
		Transactions: []blockchain.Transaction{},
		PrevHash:     latest.Hash,
		Difficulty:   c.adjustDifficulty(),
	}

	if minerAddress != "" {
		reward := blockchain.Transaction{
			ID:        generateTransactionID(minerAddress, time.Now()),
			From:      "NETWORK",
			To:        minerAddress,
			Amount:    1.0,
			Fee:       0,
			Timestamp: time.Now(),
			Nonce:     uint64(time.Now().UnixNano()),
		}
		newBlock.Transactions = append(newBlock.Transactions, reward)
	}

	// Add transactions from mempool
	for i := 0; i < 10 && len(c.mempool.txs) > 0; i++ {
		tx := c.mempool.Pop()
		if tx != nil {
			newBlock.Transactions = append(newBlock.Transactions, *tx)
		}
	}

	newBlock.Hash, newBlock.Nonce = c.proofOfWork(newBlock)
	return &newBlock
}

func generateTransactionID(seed string, timestamp time.Time) string {
	payload := []byte(seed + timestamp.String())
	return crypto.ToHex(crypto.HashDoubleSHA256(payload))
}

func (c *Consensus) proofOfWork(block blockchain.Block) (string, uint64) {
	var nonce uint64
	for {
		block.Nonce = nonce
		hash := calculateHash(block)
		if c.isValidHash(hash, block.Difficulty) {
			return hash, nonce
		}
		nonce++
	}
}

func (c *Consensus) isValidHash(hash string, difficulty uint32) bool {
	hashBytes := crypto.HashDoubleSHA256([]byte(hash))
	leadingZeros := 0
	for _, b := range hashBytes {
		leadingZeros += bits.LeadingZeros32(uint32(b)) - 24
		if b != 0 {
			break
		}
	}
	return leadingZeros >= int(difficulty)
}

func (c *Consensus) adjustDifficulty() uint32 {
	// Simple moving average for difficulty adjustment
	blocks := c.blockchain.Blocks
	if len(blocks) < 10 {
		return 1
	}
	// Placeholder: return fixed for now
	return 1
}

func calculateHash(block blockchain.Block) string {
	data, _ := json.Marshal(block)
	return crypto.ToHex(crypto.HashDoubleSHA256(data))
}

func (c *Consensus) AddToMempool(tx *blockchain.Transaction) {
	c.mempool.Push(tx)
	c.logger.Info().Str("id", tx.ID).Msg("Transaction added to mempool")
}
