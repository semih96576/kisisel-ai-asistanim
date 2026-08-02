"""
GitHub kod ve README toplayıcı — Yazılım, Elektronik projeleri
"""
import time
import json
import base64
import os
import requests
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

SEARCH_QUERIES = {
    "yazilim": [
        "machine learning tutorial",
        "deep learning implementation",
        "algorithm data structure",
        "web scraping python",
        "REST API backend",
        "neural network from scratch",
        "natural language processing",
        "computer vision opencv",
        "database orm python",
        "microservices docker",
        "trading bot python",
        "data analysis pandas",
    ],
    "elektronik": [
        "arduino project sensor",
        "raspberry pi iot",
        "ESP32 ESP8266 firmware",
        "FPGA verilog design",
        "PID controller embedded",
        "PCB design KiCad",
        "motor driver PWM",
        "STM32 HAL library",
        "oscilloscope signal analyzer",
        "power converter simulation",
    ],
    "finans": [
        "algorithmic trading strategy",
        "stock market analysis python",
        "portfolio optimization",
        "financial data analysis",
        "backtesting framework",
        "quantitative finance",
        "options pricing model",
        "forex trading bot",
    ],
    "kripto": [
        "cryptocurrency trading bot",
        "blockchain implementation python",
        "smart contract solidity",
        "DeFi protocol",
        "crypto arbitrage bot",
        "bitcoin price prediction",
        "ethereum dapp",
        "web3 python",
    ],
}

GITHUB_API = "https://api.github.com"


def get_headers():
    h = {"Accept": "application/vnd.github.v3+json",
         "User-Agent": "semihcim4.0-datacollector/1.0"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"token {GITHUB_TOKEN}"
    return h


def search_repos(query: str, language: str = "", per_page: int = 30) -> list[dict]:
    q = f"{query} stars:>10"
    if language:
        q += f" language:{language}"
    params = {"q": q, "sort": "stars", "order": "desc", "per_page": per_page}
    try:
        r = requests.get(f"{GITHUB_API}/search/repositories",
                         params=params, headers=get_headers(), timeout=15)
        if r.status_code == 403:
            print("  [UYARI] GitHub rate limit - 60 saniye bekleniyor...")
            time.sleep(60)
            return []
        r.raise_for_status()
        return r.json().get("items", [])
    except Exception as e:
        print(f"  [HATA] GitHub search '{query}': {e}")
        return []


def fetch_readme(owner: str, repo: str) -> str:
    try:
        r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/readme",
                         headers=get_headers(), timeout=10)
        if r.status_code != 200:
            return ""
        data = r.json()
        content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return content[:50000]  # Max 50KB per README
    except:
        return ""


def fetch_code_files(owner: str, repo: str, language: str) -> list[dict]:
    """Repo'daki kod dosyalarını getir."""
    ext_map = {
        "Python": [".py"],
        "JavaScript": [".js", ".ts"],
        "C++": [".cpp", ".h", ".hpp"],
        "C": [".c", ".h"],
        "Solidity": [".sol"],
        "Verilog": [".v", ".sv"],
    }
    exts = ext_map.get(language, [".py", ".js"])
    files = []
    try:
        r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/HEAD",
                         params={"recursive": 1}, headers=get_headers(), timeout=15)
        if r.status_code != 200:
            return []
        tree = r.json().get("tree", [])
        code_files = [f for f in tree
                      if f["type"] == "blob" and
                      any(f["path"].endswith(e) for e in exts) and
                      f.get("size", 0) < 100000][:10]  # Max 10 dosya/repo

        for file_info in code_files:
            time.sleep(0.2)
            fr = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{file_info['path']}",
                              headers=get_headers(), timeout=10)
            if fr.status_code != 200:
                continue
            fd = fr.json()
            content = base64.b64decode(fd.get("content", "")).decode("utf-8", errors="ignore")
            if len(content) > 200:
                files.append({"path": file_info["path"], "content": content})
    except Exception as e:
        pass
    return files


def collect(output_dir: Path, target_gb: float = 2.0) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "github.jsonl"
    target_bytes = int(target_gb * 1024 ** 3)

    seen_repos = set()
    collected_bytes = 0
    count = 0

    if out_file.exists():
        with open(out_file, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    seen_repos.add(d.get("repo_full_name", ""))
                    collected_bytes += len(line.encode("utf-8"))
                    count += 1
                except:
                    pass
        print(f"  [DEVAM] {count} repo zaten mevcut ({collected_bytes/1e6:.1f} MB)")

    with open(out_file, "a", encoding="utf-8") as f:
        for category, queries in SEARCH_QUERIES.items():
            if collected_bytes >= target_bytes:
                break
            for query in queries:
                if collected_bytes >= target_bytes:
                    break
                print(f"  [{category}] '{query}'...", end=" ", flush=True)
                repos = search_repos(query, per_page=30)
                new = 0
                for repo in repos:
                    if collected_bytes >= target_bytes:
                        break
                    full_name = repo.get("full_name", "")
                    if full_name in seen_repos:
                        continue

                    owner = repo.get("owner", {}).get("login", "")
                    repo_name = repo.get("name", "")

                    readme = fetch_readme(owner, repo_name)
                    language = repo.get("language", "Python") or "Python"
                    code_files = fetch_code_files(owner, repo_name, language)

                    # README + Kod birleştir
                    combined_text = f"# {repo.get('full_name')}\n\n"
                    if repo.get("description"):
                        combined_text += f"**{repo['description']}**\n\n"
                    if readme:
                        combined_text += f"## README\n{readme}\n\n"
                    for cf in code_files:
                        combined_text += f"## {cf['path']}\n```{language.lower()}\n{cf['content']}\n```\n\n"

                    if len(combined_text) < 300:
                        continue

                    record = {
                        "title": repo.get("full_name"),
                        "text": combined_text,
                        "description": repo.get("description", ""),
                        "language": language,
                        "stars": repo.get("stargazers_count", 0),
                        "topics": repo.get("topics", []),
                        "source": repo.get("html_url", ""),
                        "repo_full_name": full_name,
                        "category": category,
                        "domain": "github",
                    }
                    line_str = json.dumps(record, ensure_ascii=False) + "\n"
                    f.write(line_str)
                    seen_repos.add(full_name)
                    collected_bytes += len(line_str.encode("utf-8"))
                    count += 1
                    new += 1
                    time.sleep(0.5)

                print(f"✓ {new} yeni ({collected_bytes/1e6:.1f} MB)")
                time.sleep(2)

    print(f"\n  ✅ GitHub: {count} repo, {collected_bytes/1e6:.1f} MB")
    return count
