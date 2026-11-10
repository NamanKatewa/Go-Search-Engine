package bloom

import (
	"fmt"
	"testing"
)

func TestBloomFilterBasic(t *testing.T) {
	bf := New(1000, 0.01)

	urls := []string{
		"https://golang.org",
		"https://wails.io",
		"https://pkg.go.dev",
		"https://github.com",
	}

	for _, u := range urls {
		if bf.Contains(u) {
			t.Fatalf("expected %s to NOT be in filter initially", u)
		}
		added := bf.AddIfNotPresent(u)
		if !added {
			t.Fatalf("expected AddIfNotPresent to return true for new item %s", u)
		}
	}

	// Verify all present
	for _, u := range urls {
		if !bf.Contains(u) {
			t.Fatalf("expected %s to be present in filter", u)
		}
		// Second add should return false
		if bf.AddIfNotPresent(u) {
			t.Fatalf("expected AddIfNotPresent to return false for already present item %s", u)
		}
	}

	if bf.Count() != 4 {
		t.Fatalf("expected count 4, got %d", bf.Count())
	}
}

func TestBloomFilterFalsePositiveBound(t *testing.T) {
	n := uint64(5000)
	targetFP := 0.01
	bf := New(n, targetFP)

	// Add 5000 items
	for i := uint64(0); i < n; i++ {
		bf.Add(fmt.Sprintf("https://example.com/page/%d", i))
	}

	// Test 5000 non-existent items
	falsePositives := 0
	for i := uint64(0); i < n; i++ {
		if bf.Contains(fmt.Sprintf("https://different-domain.org/test/%d", i)) {
			falsePositives++
		}
	}

	measuredFP := float64(falsePositives) / float64(n)
	t.Logf("Target FP: %.4f | Measured FP: %.4f (%d/%d) | Est FP: %.4f | Memory: %d bytes",
		targetFP, measuredFP, falsePositives, n, bf.EstimatedFPRate(), bf.MemoryBytes())

	// Should be reasonably close to target false positive rate (allow minor statistical slack up to 2x target)
	if measuredFP > targetFP*2.5 {
		t.Fatalf("measured false positive rate %.4f exceeded allowed threshold", measuredFP)
	}
}
