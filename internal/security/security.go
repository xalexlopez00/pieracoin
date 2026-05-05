package security

import (
	"crypto/ecdsa"
	"crypto/sha256"
	"errors"
	"fmt"

	"pieracoin/internal/blockchain"

	"github.com/rs/zerolog"
)

type Security struct {
	logger     zerolog.Logger
	usedNonces map[uint64]bool
}

func NewSecurity(logger zerolog.Logger) *Security {
	return &Security{
		logger:     logger,
		usedNonces: make(map[uint64]bool),
	}
}

func (s *Security) ValidateTransaction(tx *blockchain.Transaction, pubKey *ecdsa.PublicKey) error {
	// Replay protection
	if s.usedNonces[tx.Nonce] {
		return errors.New("nonce already used")
	}
	s.usedNonces[tx.Nonce] = true

	// Verify signature
	data := tx.ID + tx.From + tx.To + fmt.Sprintf("%.8f", tx.Amount) + fmt.Sprintf("%.8f", tx.Fee) + tx.Timestamp.String() + fmt.Sprintf("%d", tx.Nonce)
	hash := sha256.Sum256([]byte(data))
	if !ecdsa.VerifyASN1(pubKey, hash[:], []byte(tx.Signature)) {
		return errors.New("invalid signature")
	}

	return nil
}

func (s *Security) ValidateMultiSig(tx *blockchain.Transaction, pubKeys []*ecdsa.PublicKey, required int) error {
	// Simplified multi-sig: check if at least 'required' signatures are valid
	validSigs := 0
	for _, pubKey := range pubKeys {
		if s.ValidateTransaction(tx, pubKey) == nil {
			validSigs++
		}
	}
	if validSigs < required {
		return errors.New("insufficient valid signatures")
	}
	return nil
}
