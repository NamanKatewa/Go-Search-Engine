package crawler

import (
	"bufio"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// RobotsChecker manages domain-level robots.txt policies with in-memory caching.
type RobotsChecker struct {
	mu     sync.RWMutex
	cache  map[string][]string // host -> disallowed prefixes
	client *http.Client
}

// NewRobotsChecker initializes a checker with an HTTP client timeout.
func NewRobotsChecker() *RobotsChecker {
	return &RobotsChecker{
		cache: make(map[string][]string),
		client: &http.Client{
			Timeout: 5 * time.Second,
		},
	}
}

// IsAllowed checks if an absolute URL is allowed by the host's robots.txt rules.
func (rc *RobotsChecker) IsAllowed(targetURL string) bool {
	u, err := url.Parse(targetURL)
	if err != nil {
		return false
	}

	host := u.Host
	rc.mu.RLock()
	disallowed, cached := rc.cache[host]
	rc.mu.RUnlock()

	if !cached {
		disallowed = rc.fetchRobots(u)
		rc.mu.Lock()
		rc.cache[host] = disallowed
		rc.mu.Unlock()
	}

	path := u.Path
	if path == "" {
		path = "/"
	}

	for _, prefix := range disallowed {
		if strings.HasPrefix(path, prefix) {
			return false
		}
	}
	return true
}

func (rc *RobotsChecker) fetchRobots(u *url.URL) []string {
	robotsURL := fmt.Sprintf("%s://%s/robots.txt", u.Scheme, u.Host)
	req, err := http.NewRequest("GET", robotsURL, nil)
	if err != nil {
		return nil
	}
	req.Header.Set("User-Agent", "GoSearchEngineBot/1.0 (+http://localhost)")

	resp, err := rc.client.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		return nil // If robots.txt doesn't exist or fails, allow all
	}
	defer resp.Body.Close()

	var disallowed []string
	scanner := bufio.NewScanner(io.LimitReader(resp.Body, 64*1024)) // limit to 64KB
	isWildcardAgent := false

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if idx := strings.Index(line, "#"); idx != -1 {
			line = strings.TrimSpace(line[:idx])
		}
		if line == "" {
			continue
		}

		parts := strings.SplitN(line, ":", 2)
		if len(parts) != 2 {
			continue
		}

		key := strings.ToLower(strings.TrimSpace(parts[0]))
		val := strings.TrimSpace(parts[1])

		if key == "user-agent" {
			agent := strings.ToLower(val)
			isWildcardAgent = (agent == "*" || strings.Contains(agent, "gosearchengine"))
		} else if key == "disallow" && isWildcardAgent {
			if val != "" {
				disallowed = append(disallowed, val)
			}
		}
	}

	return disallowed
}
