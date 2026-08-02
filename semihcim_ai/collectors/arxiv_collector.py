"""
arXiv akademik makale toplayıcı — CS, EE, Finance, Crypto
"""
import time
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

SEARCH_QUERIES = {
    "elektronik_elektrik": [
        "power electronics converter design",
        "embedded systems real-time control",
        "signal processing filter design",
        "FPGA implementation digital circuit",
        "motor control algorithm",
        "wireless communication protocol",
        "analog circuit design optimization",
        "sensor fusion algorithm",
        "battery management system",
        "photovoltaic solar energy system",
    ],
    "yazilim": [
        "machine learning deep learning survey",
        "transformer attention mechanism NLP",
        "reinforcement learning policy optimization",
        "graph neural network",
        "large language model training",
        "computer vision object detection",
        "federated learning privacy",
        "code generation language model",
        "software testing automation",
        "distributed systems consensus",
        "database query optimization",
        "operating system scheduling",
    ],
    "finans": [
        "portfolio optimization financial market",
        "algorithmic trading strategy",
        "risk management financial derivatives",
        "stock price prediction neural network",
        "high frequency trading market microstructure",
        "option pricing stochastic model",
        "credit risk default prediction",
        "time series forecasting financial",
        "factor model asset pricing",
        "market sentiment analysis",
    ],
    "kripto": [
        "blockchain consensus mechanism",
        "cryptocurrency price prediction",
        "smart contract security vulnerability",
        "decentralized finance DeFi protocol",
        "zero knowledge proof blockchain",
        "Bitcoin transaction analysis",
        "Ethereum gas optimization",
        "NFT market analysis",
        "layer 2 scaling solution",
        "crypto exchange liquidity",
    ],
}

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def fetch_papers(query: str, category: str, max_results: int = 50) -> list[dict]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    papers = []
    try:
        r = requests.get(ARXIV_API, params=params, timeout=30,
                         headers={"User-Agent": "semihcim4.0-datacollector/1.0"})
        r.raise_for_status()
        root = ET.fromstring(r.text)
        for entry in root.findall("atom:entry", NS):
            title_el = entry.find("atom:title", NS)
            summary_el = entry.find("atom:summary", NS)
            published_el = entry.find("atom:published", NS)
            id_el = entry.find("atom:id", NS)
            authors = [a.find("atom:name", NS).text
                       for a in entry.findall("atom:author", NS)
                       if a.find("atom:name", NS) is not None]
            cats = [c.get("term", "") for c in entry.findall("atom:category", NS)]

            if title_el is None or summary_el is None:
                continue

            title = title_el.text.strip().replace("\n", " ")
            summary = summary_el.text.strip().replace("\n", " ")

            if len(summary) < 200:
                continue

            papers.append({
                "title": title,
                "abstract": summary,
                "authors": authors[:10],
                "published": published_el.text[:10] if published_el is not None else "",
                "arxiv_id": id_el.text.split("/abs/")[-1] if id_el is not None else "",
                "source": id_el.text if id_el is not None else "",
                "arxiv_cats": cats[:5],
                "category": category,
                "domain": "arxiv",
                "text": f"Title: {title}\n\nAbstract: {summary}\n\nAuthors: {', '.join(authors)}",
            })
    except Exception as e:
        print(f"  [HATA] arXiv query '{query}': {e}")
    return papers


def collect(output_dir: Path, target_gb: float = 1.5) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "arxiv.jsonl"
    target_bytes = int(target_gb * 1024 ** 3)

    seen_ids = set()
    collected_bytes = 0
    count = 0

    if out_file.exists():
        with open(out_file, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    seen_ids.add(d.get("arxiv_id", ""))
                    collected_bytes += len(line.encode("utf-8"))
                    count += 1
                except:
                    pass
        print(f"  [DEVAM] {count} makale zaten mevcut ({collected_bytes/1e6:.1f} MB)")

    with open(out_file, "a", encoding="utf-8") as f:
        for category, queries in SEARCH_QUERIES.items():
            if collected_bytes >= target_bytes:
                break
            for query in queries:
                if collected_bytes >= target_bytes:
                    break
                print(f"  [{category}] '{query}'...", end=" ", flush=True)
                papers = fetch_papers(query, category, max_results=100)
                new = 0
                for paper in papers:
                    arxiv_id = paper["arxiv_id"]
                    if arxiv_id and arxiv_id in seen_ids:
                        continue
                    line = json.dumps(paper, ensure_ascii=False) + "\n"
                    f.write(line)
                    seen_ids.add(arxiv_id)
                    collected_bytes += len(line.encode("utf-8"))
                    count += 1
                    new += 1
                print(f"✓ {new} yeni ({collected_bytes/1e6:.1f} MB)")
                time.sleep(3)  # arXiv rate limit

    print(f"\n  ✅ arXiv: {count} makale, {collected_bytes/1e6:.1f} MB")
    return count
