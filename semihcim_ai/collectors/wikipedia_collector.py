"""
Wikipedia veri toplayıcı — Elektrik/Elektronik, Yazılım, Finans, Kripto
"""
import time
import json
import random
import requests
from pathlib import Path

TOPICS = {
    "elektronik_elektrik": [
        "Electronics", "Electrical engineering", "Transistor", "Integrated circuit",
        "Microcontroller", "Arduino", "Raspberry Pi", "Field-effect transistor",
        "Operational amplifier", "Signal processing", "Power electronics",
        "Semiconductor", "Diode", "Capacitor", "Resistor", "Inductor",
        "Oscilloscope", "Multimeter", "PCB design", "Printed circuit board",
        "Embedded system", "Digital electronics", "Analog electronics",
        "Kirchhoff's laws", "Ohm's law", "Fourier transform", "Laplace transform",
        "Electric motor", "Generator", "Transformer", "Power supply",
        "Battery", "Solar cell", "LED", "OLED", "LCD display",
        "Microprocessor", "FPGA", "PIC microcontroller", "STM32",
        "Communication protocol", "I2C", "SPI", "UART", "USB", "Ethernet",
        "Antenna", "Radio frequency", "Modulation", "Amplifier",
        "Filter (signal processing)", "Voltage regulator", "Inverter",
        "Motor controller", "PID controller", "Sensor", "Actuator",
        "Internet of Things", "Smart grid", "Electric vehicle", "MOSFET",
        "BJT transistor", "IGBT", "Thyristor", "Relay", "Circuit breaker",
        "Oscillator", "Phase-locked loop", "ADC", "DAC",
    ],
    "yazilim": [
        "Python (programming language)", "JavaScript", "C++", "Java (programming language)",
        "Rust (programming language)", "Go (programming language)", "TypeScript",
        "Algorithm", "Data structure", "Machine learning", "Deep learning",
        "Neural network", "Convolutional neural network", "Transformer (deep learning)",
        "Natural language processing", "Computer vision", "Reinforcement learning",
        "Operating system", "Linux", "Docker", "Kubernetes", "Git",
        "Database", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis",
        "Web development", "React (JavaScript library)", "Node.js", "Django",
        "API", "REST", "GraphQL", "Microservices", "Cloud computing",
        "Amazon Web Services", "Google Cloud", "Microsoft Azure",
        "Cryptography", "Cybersecurity", "Encryption", "Hash function",
        "Sorting algorithm", "Search algorithm", "Graph theory",
        "Compiler", "Interpreter", "Virtual machine", "Assembly language",
        "Design pattern", "Object-oriented programming", "Functional programming",
        "Binary tree", "Linked list", "Hash table", "Stack (abstract data type)",
        "Queue (abstract data type)", "Dynamic programming", "Big O notation",
        "Computer network", "TCP/IP", "HTTP", "WebSocket",
        "Artificial intelligence", "Chatbot", "Large language model",
        "GPT (language model)", "BERT (language model)", "Attention mechanism",
    ],
    "finans": [
        "Finance", "Stock market", "Investment", "Portfolio management",
        "Financial analysis", "Technical analysis", "Fundamental analysis",
        "Stock", "Bond (finance)", "Derivative (finance)", "Option (finance)",
        "Futures contract", "Hedge fund", "Mutual fund", "ETF",
        "Interest rate", "Inflation", "GDP", "Monetary policy",
        "Central bank", "Federal Reserve", "European Central Bank",
        "Banking", "Commercial bank", "Investment banking",
        "Valuation (finance)", "P/E ratio", "Discounted cash flow",
        "Risk management", "Diversification (finance)", "Asset allocation",
        "Bull market", "Bear market", "Market capitalization",
        "Dividend", "Earnings per share", "Balance sheet",
        "Income statement", "Cash flow statement", "Financial ratio",
        "Return on investment", "Compound interest", "Time value of money",
        "Capital market", "Money market", "Foreign exchange market",
        "Quantitative finance", "Algorithmic trading", "High-frequency trading",
        "Black–Scholes model", "Value at risk", "Monte Carlo method",
        "Economic cycle", "Recession", "Financial crisis", "Subprime crisis",
        "Warren Buffett", "Benjamin Graham", "Value investing",
        "Growth investing", "Index fund", "Passive investing",
    ],
    "kripto": [
        "Cryptocurrency", "Bitcoin", "Ethereum", "Blockchain",
        "Decentralized finance", "Smart contract", "Solidity (programming language)",
        "Web3", "Non-fungible token", "Decentralized exchange",
        "Proof of work", "Proof of stake", "Consensus mechanism",
        "Mining (cryptocurrency)", "Cryptocurrency wallet", "Public key cryptography",
        "Hash function", "Merkle tree", "Digital signature",
        "Satoshi Nakamoto", "Vitalik Buterin", "Ethereum Virtual Machine",
        "DeFi", "Yield farming", "Liquidity pool", "Automated market maker",
        "Uniswap", "Aave", "Compound (finance)", "MakerDAO",
        "Stablecoin", "USDT", "USDC", "DAI (cryptocurrency)",
        "Layer 2 scaling", "Lightning Network", "Polygon (blockchain)",
        "Solana", "Cardano", "Polkadot", "Avalanche (blockchain)",
        "Initial coin offering", "Token (cryptocurrency)", "Altcoin",
        "Cryptocurrency exchange", "Coinbase", "Binance",
        "Cold wallet", "Hot wallet", "Seed phrase", "Private key",
        "51% attack", "Double-spending", "Cryptographic hash",
        "Zero-knowledge proof", "Rollup (cryptocurrency)",
    ],
}

WIKI_API = "https://en.wikipedia.org/w/api.php"
TR_WIKI_API = "https://tr.wikipedia.org/w/api.php"


def fetch_article(title: str, lang: str = "en") -> dict | None:
    api = TR_WIKI_API if lang == "tr" else WIKI_API
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts|categories|links",
        "explaintext": True,
        "exsectionformat": "plain",
        "redirects": 1,
        "pllimit": 50,
    }
    try:
        r = requests.get(api, params=params, timeout=15,
                         headers={"User-Agent": "semihcim4.0-datacollector/1.0"})
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if "missing" in page:
                return None
            text = page.get("extract", "")
            if len(text) < 500:
                return None
            cats = [c["title"].replace("Category:", "")
                    for c in page.get("categories", [])]
            links = [lk["title"] for lk in page.get("links", [])]
            return {
                "title": page["title"],
                "text": text,
                "categories": cats[:20],
                "related": links[:30],
                "source": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "lang": lang,
            }
    except Exception as e:
        print(f"  [HATA] {title}: {e}")
    return None


def fetch_search_results(query: str, limit: int = 10) -> list[str]:
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srnamespace": 0,
    }
    try:
        r = requests.get(WIKI_API, params=params, timeout=10,
                         headers={"User-Agent": "semihcim4.0-datacollector/1.0"})
        results = r.json().get("query", {}).get("search", [])
        return [res["title"] for res in results]
    except:
        return []


def collect(output_dir: Path, target_gb: float = 2.0) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "wikipedia.jsonl"
    target_bytes = int(target_gb * 1024 ** 3)

    seen = set()
    collected_bytes = 0
    count = 0

    # Önceki ilerlemeyi yükle
    if out_file.exists():
        with open(out_file, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    seen.add(d["title"])
                    collected_bytes += len(line.encode("utf-8"))
                    count += 1
                except:
                    pass
        print(f"  [DEVAM] {count} makale zaten mevcut ({collected_bytes/1e6:.1f} MB)")

    # Tüm konuları karıştır
    all_titles = []
    for category, titles in TOPICS.items():
        for t in titles:
            all_titles.append((category, t))
    random.shuffle(all_titles)

    with open(out_file, "a", encoding="utf-8") as f:
        # 1. Önce bilinen başlıkları topla
        for category, title in all_titles:
            if collected_bytes >= target_bytes:
                break
            if title in seen:
                continue

            print(f"  [{category}] {title}...", end=" ", flush=True)
            article = fetch_article(title)
            if article:
                article["category"] = category
                article["domain"] = "wikipedia"
                line = json.dumps(article, ensure_ascii=False) + "\n"
                f.write(line)
                seen.add(title)
                collected_bytes += len(line.encode("utf-8"))
                count += 1
                print(f"✓ {len(article['text'])//1000}K karakter")

                # İlgili makaleleri de ekle
                for related in article.get("related", [])[:5]:
                    if related not in seen and collected_bytes < target_bytes:
                        time.sleep(0.3)
                        rel = fetch_article(related)
                        if rel:
                            rel["category"] = category
                            rel["domain"] = "wikipedia"
                            line2 = json.dumps(rel, ensure_ascii=False) + "\n"
                            f.write(line2)
                            seen.add(related)
                            collected_bytes += len(line2.encode("utf-8"))
                            count += 1
            else:
                print("✗")

            time.sleep(random.uniform(0.5, 1.2))

        # 2. Arama ile daha fazla içerik bul
        search_queries = [
            "electronic circuit design tutorial",
            "machine learning algorithms explained",
            "cryptocurrency trading strategies",
            "stock market analysis methods",
            "embedded systems programming",
            "DeFi protocols explained",
            "power electronics converters",
            "algorithmic trading Python",
            "blockchain technology applications",
            "signal processing techniques",
            "financial derivatives pricing",
            "deep learning architectures",
        ]
        for query in search_queries:
            if collected_bytes >= target_bytes:
                break
            titles = fetch_search_results(query, limit=20)
            for title in titles:
                if title not in seen and collected_bytes < target_bytes:
                    article = fetch_article(title)
                    if article:
                        article["category"] = "search"
                        article["domain"] = "wikipedia"
                        line = json.dumps(article, ensure_ascii=False) + "\n"
                        f.write(line)
                        seen.add(title)
                        collected_bytes += len(line.encode("utf-8"))
                        count += 1
                    time.sleep(0.4)

    print(f"\n  ✅ Wikipedia: {count} makale, {collected_bytes/1e6:.1f} MB")
    return count
