package crypto

import (
	"crypto/sha256"
	"encoding/hex"
	"golang.org/x/crypto/ripemd160"
)

// HashSHA256 computes SHA256 hash
func HashSHA256(data []byte) []byte {
	hash := sha256.Sum256(data)
	return hash[:]
}

// HashDoubleSHA256 computes double SHA256 hash
func HashDoubleSHA256(data []byte) []byte {
	first := HashSHA256(data)
	return HashSHA256(first)
}

// HashRIPEMD160 computes RIPEMD160 hash
func HashRIPEMD160(data []byte) []byte {
	hasher := ripemd160.New()
	hasher.Write(data)
	return hasher.Sum(nil)
}

// ToHex converts bytes to hex string
func ToHex(data []byte) string {
	return hex.EncodeToString(data)
}

// FromHex converts hex string to bytes
func FromHex(str string) ([]byte, error) {
	return hex.DecodeString(str)
}