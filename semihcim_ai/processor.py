"""
Veri işleme, temizleme, tekilleştirme ve eğitim formatına dönüştürme
"""
import json
import re
import hashlib
from pathlib import Path
from collections import Counter


def clean_text(text: str) -> str:
    """Metni temizle ve normalize et."""
    if not text:
        return ""
    # Çok fazla boşluk/newline temizle
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r' {3,}', ' ', text)
    text = re.sub(r'\t', ' ', text)
    # Encoding artifacts
    text = text.replace('\x00', '').replace('\ufffd', '')
    # HTML kalıntıları
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    return text.strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8"))[:16].hexdigest()[:16]


def is_quality(record: dict, min_chars: int = 300) -> bool:
    """Kalite filtresi."""
    text = record.get("text", "")
    if len(text) < min_chars:
        return False
    # Çok fazla tekrar eden karakter
    if len(set(text)) < 20:
        return False
    # Sadece sayı/sembol
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    if alpha_ratio < 0.3:
        return False
    return True


def chunk_text(text: str, max_chars: int = 4000, overlap: int = 200) -> list[str]:
    """Uzun metinleri örtüşen parçalara böl."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end < len(text):
            # Paragraf veya cümle sonunda kes
            newline = text.rfind('\n', start, end)
            period = text.rfind('. ', start, end)
            cut = max(newline, period)
            if cut > start + max_chars // 2:
                end = cut + 1
        chunk = text[start:end].strip()
        if len(chunk) > 100:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def to_training_format(record: dict, mode: str = "instruct") -> list[dict]:
    """
    Veriyi eğitim formatına dönüştür.

    mode:
      "pretrain" → ham metin
      "instruct" → soru-cevap formatı
    """
    text = clean_text(record.get("text", ""))
    title = record.get("title", "")
    category = record.get("category", "genel")
    domain = record.get("domain", "web")

    if not text or len(text) < 200:
        return []

    results = []

    if mode == "pretrain":
        # Ham metin — dil modeli pretraining için
        chunks = chunk_text(text, max_chars=2048)
        for chunk in chunks:
            results.append({
                "text": chunk,
                "category": category,
                "domain": domain,
            })

    elif mode == "instruct":
        # Soru-cevap formatı — instruction tuning için
        chunks = chunk_text(text, max_chars=3000)

        # Ana içerik soruları
        questions = _generate_questions(title, category, domain)
        for i, chunk in enumerate(chunks[:3]):  # İlk 3 chunk
            for q in questions[:2]:
                results.append({
                    "instruction": q,
                    "input": "",
                    "output": chunk,
                    "category": category,
                    "domain": domain,
                })

        # Özet sorusu
        if len(text) > 500:
            results.append({
                "instruction": f"'{title}' konusunu kısaca özetle.",
                "input": "",
                "output": text[:800],
                "category": category,
                "domain": domain,
            })

    return results


def _generate_questions(title: str, category: str, domain: str) -> list[str]:
    """Başlığa ve kategoriye göre soru üret."""
    questions = [f"{title} hakkında ne biliyorsun?"]

    cat_questions = {
        "elektronik_elektrik": [
            f"{title} nasıl çalışır?",
            f"{title} devre analizi nasıl yapılır?",
            f"{title} için pratik uygulama örnekleri nelerdir?",
        ],
        "elektronik": [
            f"{title} nasıl kullanılır?",
            f"{title} için kod örneği yazar mısın?",
        ],
        "yazilim": [
            f"{title} nasıl implement edilir?",
            f"{title} için Python kodu yazar mısın?",
            f"{title} algoritmik karmaşıklığı nedir?",
        ],
        "finans": [
            f"{title} yatırım açısından nasıl değerlendirirsin?",
            f"{title} risk analizi nasıl yapılır?",
            f"{title} stratejisi nedir?",
        ],
        "kripto": [
            f"{title} nasıl çalışır?",
            f"{title} güvenli mi, riskleri nelerdir?",
            f"{title} teknik analizi nasıl yapılır?",
        ],
    }

    questions.extend(cat_questions.get(category, [f"{title} ne anlama gelir?"]))
    return questions


def process_all(raw_dir: Path, processed_dir: Path, mode: str = "instruct") -> dict:
    """Tüm ham veriyi işle."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_file = processed_dir / f"training_{mode}.jsonl"

    stats = {"total_raw": 0, "total_processed": 0, "skipped": 0,
             "duplicates": 0, "by_category": Counter(), "total_bytes": 0}

    seen_hashes = set()

    with open(out_file, "w", encoding="utf-8") as out_f:
        for jsonl_file in sorted(raw_dir.glob("*.jsonl")):
            print(f"\n  İşleniyor: {jsonl_file.name}")
            file_count = 0
            with open(jsonl_file, encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    stats["total_raw"] += 1

                    # Kalite filtresi
                    if not is_quality(record):
                        stats["skipped"] += 1
                        continue

                    # Tekilleştirme
                    text = record.get("text", "")
                    h = hashlib.md5(text[:500].encode("utf-8")).hexdigest()
                    if h in seen_hashes:
                        stats["duplicates"] += 1
                        continue
                    seen_hashes.add(h)

                    # Formata dönüştür
                    training_items = to_training_format(record, mode=mode)
                    for item in training_items:
                        line_out = json.dumps(item, ensure_ascii=False) + "\n"
                        out_f.write(line_out)
                        stats["total_processed"] += 1
                        stats["by_category"][record.get("category", "other")] += 1
                        stats["total_bytes"] += len(line_out.encode("utf-8"))
                        file_count += 1

            print(f"    → {file_count} eğitim örneği oluşturuldu")

    print(f"\n{'='*50}")
    print(f"  TOPLAM İŞLENEN: {stats['total_raw']} raw kayıt")
    print(f"  EĞİTİM ÖRNEĞİ: {stats['total_processed']}")
    print(f"  ATLANAN: {stats['skipped']} (kalite filtresi)")
    print(f"  TEKRAR: {stats['duplicates']}")
    print(f"  BOYUT: {stats['total_bytes']/1e6:.1f} MB")
    print(f"\n  Kategori dağılımı:")
    for cat, cnt in stats["by_category"].most_common():
        print(f"    {cat}: {cnt}")

    # İstatistikleri kaydet
    with open(processed_dir / "stats.json", "w") as f:
        json.dump({**stats, "by_category": dict(stats["by_category"])}, f, indent=2)

    return stats


def split_train_val(processed_dir: Path, val_ratio: float = 0.05):
    """Train/validation bölünmesi yap."""
    import random
    src = processed_dir / "training_instruct.jsonl"
    if not src.exists():
        print("Önce process_all() çalıştır!")
        return

    all_lines = src.read_text(encoding="utf-8").strip().split("\n")
    random.shuffle(all_lines)
    val_size = int(len(all_lines) * val_ratio)

    val_lines = all_lines[:val_size]
    train_lines = all_lines[val_size:]

    (processed_dir / "train.jsonl").write_text("\n".join(train_lines), encoding="utf-8")
    (processed_dir / "val.jsonl").write_text("\n".join(val_lines), encoding="utf-8")

    print(f"  Train: {len(train_lines)} örnek")
    print(f"  Val:   {len(val_lines)} örnek")


if __name__ == "__main__":
    base = Path(__file__).parent
    raw_dir = base / "data" / "raw"
    processed_dir = base / "data" / "processed"

    print("🔄 Veri işleniyor...")
    stats = process_all(raw_dir, processed_dir, mode="instruct")
    print("\n✂️ Train/Val bölünüyor...")
    split_train_val(processed_dir)
    print("\n✅ Veri işleme tamamlandı!")
