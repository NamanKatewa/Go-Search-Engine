package main

import (
	"embed"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"strconv"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
	"github.com/wailsapp/wails/v2/pkg/options/windows"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	webMode := flag.Bool("web", false, "Start in local web server mode instead of native desktop window")
	port := flag.Int("port", 34115, "Port for web mode server")
	flag.Parse()

	app := NewApp()

	if *webMode {
		runWebServer(app, *port)
		return
	}

	// Create application with options
	err := wails.Run(&options.App{
		Title:     "Go Desktop Search Engine",
		Width:     1280,
		Height:    860,
		MinWidth:  1024,
		MinHeight: 700,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		BackgroundColour: &options.RGBA{R: 15, G: 23, B: 42, A: 1}, // Slate 900
		OnStartup:        app.startup,
		OnShutdown:       app.shutdown,
		Bind: []interface{}{
			app,
		},
		Windows: &windows.Options{
			WebviewIsTransparent: false,
			WindowIsTranslucent:  false,
			BackdropType:         windows.Mica,
		},
	})

	if err != nil {
		log.Println("Wails desktop launch returned:", err)
		log.Println("Starting web interface fallback on port", *port)
		runWebServer(app, *port)
	}
}

func runWebServer(app *App, port int) {
	mux := http.NewServeMux()

	// Static asset handler
	distFS, err := fs.Sub(assets, "frontend/dist")
	if err == nil {
		mux.Handle("/", http.FileServer(http.FS(distFS)))
	} else {
		mux.Handle("/", http.FileServer(http.Dir("frontend/dist")))
	}

	// REST API endpoints for browser/test compatibility
	mux.HandleFunc("/api/crawl/start", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req struct {
			SeedURL     string `json:"seedUrl"`
			MaxPages    int    `json:"maxPages"`
			Concurrency int    `json:"concurrency"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		res := app.StartCrawl(req.SeedURL, req.MaxPages, req.Concurrency)
		json.NewEncoder(w).Encode(map[string]string{"message": res})
	})

	mux.HandleFunc("/api/crawl/stop", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		res := app.StopCrawl()
		json.NewEncoder(w).Encode(map[string]string{"message": res})
	})

	mux.HandleFunc("/api/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		metrics := app.GetMetrics()
		json.NewEncoder(w).Encode(metrics)
	})

	mux.HandleFunc("/api/search", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		q := r.URL.Query().Get("q")
		limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
		if limit <= 0 {
			limit = 20
		}
		results, err := app.Search(q, limit)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(results)
	})

	mux.HandleFunc("/api/stats", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		stats, err := app.GetStats()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(stats)
	})

	addr := fmt.Sprintf("127.0.0.1:%d", port)
	fmt.Printf("\n======================================================\n")
	fmt.Printf(" Go Desktop Search Engine - Web Interface Running\n")
	fmt.Printf(" Open in browser: http://%s\n", addr)
	fmt.Printf("======================================================\n\n")

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
