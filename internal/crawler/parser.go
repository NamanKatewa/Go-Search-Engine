package crawler

import (
	"bytes"
	"net/url"
	"regexp"
	"strings"

	"golang.org/x/net/html"
)

var (
	whitespaceRegex  = regexp.MustCompile(`\s+`)
	wordExtractRegex = regexp.MustCompile(`[a-zA-Z0-9]{2,45}`)
)

// ExtractedPage contains the parsed content and discovered links of an HTML page.
type ExtractedPage struct {
	Title     string
	Snippet   string
	WordCount int
	Terms     map[string]int
	Links     []string
}

// ExtractContent parses raw HTML bytes, strips boilerplate/navigation noise using a readability heuristic,
// computes term frequencies, and extracts absolute outgoing links.
func ExtractContent(rawHTML []byte, baseURL *url.URL) (*ExtractedPage, error) {
	doc, err := html.Parse(bytes.NewReader(rawHTML))
	if err != nil {
		return nil, err
	}

	var title string
	var links []string
	var textBuf bytes.Buffer

	// Traverse DOM to find title, links, and collect clean body text
	var traverse func(*html.Node, bool)
	traverse = func(n *html.Node, insideIgnoredTag bool) {
		if n.Type == html.ElementNode {
			tag := strings.ToLower(n.Data)

			// Strip noisy layout and script tags (Readability heuristic)
			switch tag {
			case "script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "iframe":
				insideIgnoredTag = true
			case "title":
				if title == "" && n.FirstChild != nil {
					title = strings.TrimSpace(n.FirstChild.Data)
				}
			case "a":
				for _, attr := range n.Attr {
					if strings.ToLower(attr.Key) == "href" {
						link := cleanAndResolveURL(attr.Val, baseURL)
						if link != "" {
							links = append(links, link)
						}
					}
				}
			}
		}

		if n.Type == html.TextNode && !insideIgnoredTag {
			text := strings.TrimSpace(n.Data)
			if len(text) > 0 {
				textBuf.WriteString(text)
				textBuf.WriteString(" ")
			}
		}

		for c := n.FirstChild; c != nil; c = c.NextSibling {
			traverse(c, insideIgnoredTag)
		}
	}

	traverse(doc, false)

	if title == "" {
		title = baseURL.String()
	}

	cleanText := whitespaceRegex.ReplaceAllString(textBuf.String(), " ")
	cleanText = strings.TrimSpace(cleanText)

	// Build snippet for search results (first 200 characters)
	snippet := cleanText
	if len(snippet) > 220 {
		snippet = snippet[:220] + "..."
	}

	// Tokenize words and calculate Term Frequencies (TF)
	words := wordExtractRegex.FindAllString(strings.ToLower(cleanText), -1)
	terms := make(map[string]int)
	for _, w := range words {
		// Filter short terms
		if len(w) >= 2 {
			terms[w]++
		}
	}

	return &ExtractedPage{
		Title:     title,
		Snippet:   snippet,
		WordCount: len(words),
		Terms:     terms,
		Links:     links,
	}, nil
}

// cleanAndResolveURL normalizes links and resolves relative paths to absolute URLs.
func cleanAndResolveURL(rawLink string, base *url.URL) string {
	rawLink = strings.TrimSpace(rawLink)
	if rawLink == "" || strings.HasPrefix(rawLink, "javascript:") || strings.HasPrefix(rawLink, "mailto:") || strings.HasPrefix(rawLink, "tel:") {
		return ""
	}

	u, err := url.Parse(rawLink)
	if err != nil {
		return ""
	}

	resolved := base.ResolveReference(u)
	if resolved.Scheme != "http" && resolved.Scheme != "https" {
		return ""
	}

	// Remove hash fragments and trailing slashes for canonicalization
	resolved.Fragment = ""
	normalized := resolved.String()
	return strings.TrimRight(normalized, "/")
}
