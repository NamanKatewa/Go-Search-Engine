import sqlite3, os, re, json, urllib.request, urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "internal", "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "seed.db")

print(f"Target DB destination: {DB_PATH}")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("PRAGMA page_size = 4096;")
c.execute("PRAGMA journal_mode = OFF;")
c.execute("PRAGMA synchronous = OFF;")

c.execute("""
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    snippet TEXT NOT NULL DEFAULT '',
    word_count INTEGER NOT NULL DEFAULT 0,
    crawled_at DATETIME NOT NULL
);
""")
c.execute("CREATE TABLE terms (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT NOT NULL UNIQUE);")
c.execute("CREATE TABLE document_terms (term_id INTEGER NOT NULL, document_id INTEGER NOT NULL, term_frequency INTEGER NOT NULL, PRIMARY KEY (term_id, document_id));")

word_regex = re.compile(r'[a-zA-Z0-9]{2,45}')
term_map = {}
term_id_seq = 1

doc_rows = []
doc_term_rows = []
current_doc_id = 1

# 1. Fetch Featured Wikipedia Articles across Tech, Science, CS, Math, History, AI
wiki_topics = [
    # Computer Science & Programming
    "Computer science", "Artificial intelligence", "Machine learning", "Deep learning", "Neural network",
    "Operating system", "Computer network", "Database", "Relational database", "SQL", "Distributed computing",
    "Search engine", "Web crawler", "Information retrieval", "Data structure", "Binary search tree",
    "Algorithm", "Time complexity", "Hash table", "Bloom filter", "Compiler", "Interpreter (computing)",
    "Go (programming language)", "Python (programming language)", "C (programming language)", "C++",
    "Rust (programming language)", "JavaScript", "TypeScript", "Linux", "Git", "Microservices",
    "Cloud computing", "Computer security", "Cryptography", "Public-key cryptography", "Concurrency (computer science)",
    "Thread (computing)", "Goroutine", "Parallel computing", "Software engineering", "Object-oriented programming",
    "Functional programming", "Web development", "Internet", "World Wide Web", "Hypertext Transfer Protocol",
    "Domain Name System", "IPv4", "IPv6", "Transmission Control Protocol", "User Datagram Protocol",
    "Memory management", "Virtual memory", "Computer architecture", "Central processing unit", "Graphics processing unit",
    # Science & Mathematics
    "Physics", "Quantum mechanics", "General relativity", "Mathematics", "Calculus", "Linear algebra",
    "Probability theory", "Statistics", "Discrete mathematics", "Graph theory", "Number theory",
    "Biology", "DNA", "Genetics", "Evolution", "Ecology", "Chemistry", "Organic chemistry", "Atom",
    "Periodic table", "Astronomy", "Solar System", "Galaxy", "Black hole", "Universe",
    # History & Philosophy
    "Science", "Philosophy", "Logic", "Epistemology", "Scientific method", "History of science",
    "Industrial Revolution", "Information Age", "Renaissance", "Ancient Greece"
]

print(f"Fetching {len(wiki_topics)} high-profile Wikipedia knowledge articles...")
chunk_size = 20
headers = {'User-Agent': 'GoDesktopSearchEngine/1.0 (edu@krmangalam.edu.in)'}

for i in range(0, len(wiki_topics), chunk_size):
    chunk = wiki_topics[i:i+chunk_size]
    q = '|'.join(urllib.parse.quote(t) for t in chunk)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={q}&prop=extracts&exintro=1&explaintext=1&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                title = p.get('title', '')
                extract = p.get('extract', '')
                if not extract or len(extract.strip()) < 40:
                    continue
                doc_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                snippet = extract[:200].replace('\n', ' ')
                
                tokens = [t.lower() for t in word_regex.findall(f"{title} {extract}")]
                if not tokens:
                    continue
                freqs = {}
                for t in tokens:
                    freqs[t] = freqs.get(t, 0) + 1
                
                doc_rows.append((current_doc_id, doc_url, f"Wikipedia: {title}", snippet, len(tokens), "2026-11-23 00:00:00"))
                for t, count in freqs.items():
                    if t not in term_map:
                        term_map[t] = term_id_seq
                        term_id_seq += 1
                    doc_term_rows.append((term_map[t], current_doc_id, count))
                current_doc_id += 1
    except Exception as e:
        print(f"Error fetching chunk {chunk}: {e}")

print(f"Indexed {len(doc_rows)} Wikipedia articles.")

# 2. Fetch Webster's English Dictionary (10,000 entries)
dict_url = "https://raw.githubusercontent.com/matthewreagan/WebstersEnglishDictionary/master/dictionary_compact.json"
print("Downloading Webster's Unabridged Dictionary...")
req = urllib.request.Request(dict_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    dict_data = json.loads(resp.read().decode('utf-8'))

dict_sample = list(dict_data.items())[:10000]
print(f"Processing {len(dict_sample)} dictionary entries...")

for word, definition in dict_sample:
    doc_url = f"dict://en/{word.lower()}"
    title = f"{word.capitalize()}"
    snippet = definition[:180].replace('\n', ' ')
    
    tokens = [t.lower() for t in word_regex.findall(f"{word} {definition}")]
    if not tokens:
        continue
    freqs = {}
    for t in tokens:
        freqs[t] = freqs.get(t, 0) + 1
    
    doc_rows.append((current_doc_id, doc_url, title, snippet, len(tokens), "2026-11-23 00:00:00"))
    for t, count in freqs.items():
        if t not in term_map:
            term_map[t] = term_id_seq
            term_id_seq += 1
        doc_term_rows.append((term_map[t], current_doc_id, count))
    current_doc_id += 1

print("Executing SQLite batch insert...")
c.executemany("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)", doc_rows)
c.executemany("INSERT INTO terms (id, term) VALUES (?, ?)", [(tid, t) for t, tid in term_map.items()])
c.executemany("INSERT INTO document_terms VALUES (?, ?, ?)", doc_term_rows)

print("Building indices...")
c.execute("CREATE INDEX idx_terms_term ON terms(term);")
c.execute("CREATE INDEX idx_doc_terms_term ON document_terms(term_id);")
c.execute("CREATE INDEX idx_doc_terms_doc ON document_terms(document_id);")

conn.commit()
conn.execute("VACUUM;")
conn.close()

size = os.path.getsize(DB_PATH)
print(f"Successfully generated seed database!")
print(f"Total documents: {len(doc_rows)}")
print(f"Total unique terms: {len(term_map)}")
print(f"Total postings: {len(doc_term_rows)}")
print(f"Final file size: {size / (1024*1024):.2f} MB")
