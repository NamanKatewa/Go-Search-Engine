package bloom

import (
	"hash/fnv"
	"math"
	"sync"
)

// BloomFilter is a thread-safe probabilistic data structure used to test set membership
// with zero false negatives and a mathematically bounded false positive probability.
type BloomFilter struct {
	mu     sync.RWMutex
	bits   []uint64
	m      uint64  // total number of bits
	k      uint32  // number of hash functions
	count  uint64  // elements inserted
	targetFPRate float64
}

// New creates a new BloomFilter sized for expectedElements with the desired falsePositiveRate (e.g. 0.001 for 0.1%).
func New(expectedElements uint64, falsePositiveRate float64) *BloomFilter {
	if expectedElements == 0 {
		expectedElements = 100000
	}
	if falsePositiveRate <= 0 || falsePositiveRate >= 1.0 {
		falsePositiveRate = 0.001
	}

	// Optimal m = - (n * ln(p)) / (ln(2)^2)
	ln2 := math.Ln2
	mFloat := -float64(expectedElements) * math.Log(falsePositiveRate) / (ln2 * ln2)
	m := uint64(math.Ceil(mFloat))
	if m < 64 {
		m = 64
	}

	// Optimal k = (m / n) * ln(2)
	kFloat := (float64(m) / float64(expectedElements)) * ln2
	k := uint32(math.Max(1, math.Round(kFloat)))

	// Number of uint64 words required
	words := (m + 63) / 64

	return &BloomFilter{
		bits:         make([]uint64, words),
		m:            words * 64, // Align to 64-bit word boundaries
		k:            k,
		count:        0,
		targetFPRate: falsePositiveRate,
	}
}

func fmix64(k uint64) uint64 {
	k ^= k >> 33
	k *= 0xff51afd7ed558ccd
	k ^= k >> 33
	k *= 0xc4ceb9fe1a85ec53
	k ^= k >> 33
	return k
}

// hashValues computes two distinct 64-bit hashes using FNV-1a variations to implement Kirsch-Mitzenmacher optimization.
func (bf *BloomFilter) hashValues(data []byte) (uint64, uint64) {
	// Primary FNV-1a 64-bit
	h1 := fnv.New64a()
	h1.Write(data)
	hash1 := fmix64(h1.Sum64())

	// Secondary hash with alternate salt
	h2 := fnv.New64()
	h2.Write([]byte{0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE, 0xBA, 0xBE})
	h2.Write(data)
	hash2 := fmix64(h2.Sum64())
	if hash2 == 0 {
		hash2 = 1 // Prevent degenerate zero step
	}

	return hash1, hash2
}

// Add inserts an item into the Bloom filter.
func (bf *BloomFilter) Add(item string) {
	bf.mu.Lock()
	defer bf.mu.Unlock()

	h1, h2 := bf.hashValues([]byte(item))
	for i := uint32(0); i < bf.k; i++ {
		combined := (h1 + uint64(i)*h2) % bf.m
		wordIdx := combined / 64
		bitIdx := combined % 64
		bf.bits[wordIdx] |= (1 << bitIdx)
	}
	bf.count++
}

// AddIfNotPresent tests if an item is present, and adds it if not present.
// Returns true if the item was newly added, or false if it was already (probably) present.
func (bf *BloomFilter) AddIfNotPresent(item string) bool {
	bf.mu.Lock()
	defer bf.mu.Unlock()

	h1, h2 := bf.hashValues([]byte(item))
	alreadyPresent := true

	for i := uint32(0); i < bf.k; i++ {
		combined := (h1 + uint64(i)*h2) % bf.m
		wordIdx := combined / 64
		bitIdx := combined % 64
		if (bf.bits[wordIdx] & (1 << bitIdx)) == 0 {
			alreadyPresent = false
			bf.bits[wordIdx] |= (1 << bitIdx)
		}
	}

	if !alreadyPresent {
		bf.count++
		return true
	}
	return false
}

// Contains checks whether an item is likely in the set.
// A return value of false guarantees the item has never been added.
// A return value of true indicates it is present with probability (1 - FPRate).
func (bf *BloomFilter) Contains(item string) bool {
	bf.mu.RLock()
	defer bf.mu.RUnlock()

	h1, h2 := bf.hashValues([]byte(item))
	for i := uint32(0); i < bf.k; i++ {
		combined := (h1 + uint64(i)*h2) % bf.m
		wordIdx := combined / 64
		bitIdx := combined % 64
		if (bf.bits[wordIdx] & (1 << bitIdx)) == 0 {
			return false
		}
	}
	return true
}

// Count returns the number of items added so far.
func (bf *BloomFilter) Count() uint64 {
	bf.mu.RLock()
	defer bf.mu.RUnlock()
	return bf.count
}

// MemoryBytes returns the current memory usage of the bit array in bytes.
func (bf *BloomFilter) MemoryBytes() uint64 {
	return uint64(len(bf.bits)) * 8
}

// CapacityBits returns total bits available.
func (bf *BloomFilter) CapacityBits() uint64 {
	return bf.m
}

// HashCount returns the number of hash functions k.
func (bf *BloomFilter) HashCount() uint32 {
	return bf.k
}

// EstimatedFPRate returns the current mathematical false positive probability based on occupancy.
func (bf *BloomFilter) EstimatedFPRate() float64 {
	bf.mu.RLock()
	defer bf.mu.RUnlock()
	if bf.count == 0 {
		return 0.0
	}
	// p ~ (1 - e^(-k*n/m))^k
	exponent := -float64(bf.k) * float64(bf.count) / float64(bf.m)
	return math.Pow(1.0-math.Exp(exponent), float64(bf.k))
}
