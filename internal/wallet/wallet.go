package wallet

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"math/big"

	"github.com/rs/zerolog"
	"github.com/tyler-smith/go-bip39"
)

type Wallet struct {
	logger zerolog.Logger
}

func NewWallet(logger zerolog.Logger) *Wallet {
	return &Wallet{logger: logger}
}

func (w *Wallet) GenerateMnemonic() (string, error) {
	entropy, err := bip39.NewEntropy(128) // 12 words
	if err != nil {
		return "", err
	}
	mnemonic, err := bip39.NewMnemonic(entropy)
	if err != nil {
		return "", err
	}
	return mnemonic, nil
}

// DeriveKeyFromMnemonic generates a private key from mnemonic
// Uses the seed directly to derive a key
func (w *Wallet) DeriveKeyFromMnemonic(mnemonic string) (*ecdsa.PrivateKey, error) {
	seed := bip39.NewSeed(mnemonic, "")

	// Use SHA256(seed) as the basis for the private key
	hash := sha256.Sum256(seed)

	// Create private key from hash
	privKey := &ecdsa.PrivateKey{
		PublicKey: ecdsa.PublicKey{
			Curve: elliptic.P256(),
		},
		D: new(big.Int).SetBytes(hash[:]),
	}

	// Calculate Q = d*G
	privKey.PublicKey.X, privKey.PublicKey.Y = privKey.PublicKey.Curve.ScalarBaseMult(privKey.D.Bytes())

	return privKey, nil
}

func (w *Wallet) AddressFromMnemonic(mnemonic string) (string, error) {
	privKey, err := w.DeriveKeyFromMnemonic(mnemonic)
	if err != nil {
		return "", err
	}
	pubKey := privKey.Public().(*ecdsa.PublicKey)
	return publicKeyToAddress(pubKey), nil
}

func publicKeyToAddress(pub *ecdsa.PublicKey) string {
	pubBytes := elliptic.Marshal(pub.Curve, pub.X, pub.Y)
	hash := sha256.Sum256(pubBytes)
	return hex.EncodeToString(hash[:20])
}

// GenerateRandomPrivateKey generates a random ECDSA private key
func (w *Wallet) GenerateRandomPrivateKey() (*ecdsa.PrivateKey, error) {
	return ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
}

// GetAddressFromPrivateKey derives address from a private key
func (w *Wallet) GetAddressFromPrivateKey(privKey *ecdsa.PrivateKey) string {
	pubKey := privKey.Public().(*ecdsa.PublicKey)
	return publicKeyToAddress(pubKey)
}
