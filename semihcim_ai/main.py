"""
semihcim4.0 — Ana Orkestratör
Veri Toplama → İşleme → Eğitim
"""
import sys
import time
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          semihcim4.0 — AI Eğitim Sistemi                ║
║                                                          ║
║  Elektrik/Elektronik  •  Yazılım  •  Finans  •  Kripto  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

TARGET_GB = 10.0  # Hedef veri boyutu

# Her kaynaktan ne kadar veri (GB)
SOURCE_TARGETS = {
    "wikipedia": 3.0,
    "arxiv":     2.0,
    "github":    3.0,
    "finance":   0.5,
    "knowledge": 1.5,   # Curated knowledge base
}


def print_progress(label: str, current_bytes: int, target_bytes: int):
    pct = min(100, current_bytes / target_bytes * 100)
    bar_len = 40
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    mb = current_bytes / 1e6
    target_mb = target_bytes / 1e6
    print(f"  {label:12s} [{bar}] {pct:5.1f}% ({mb:.0f}/{target_mb:.0f} MB)")


def collect_all(sources: list[str] = None):
    """Tüm kaynaklardan veri topla."""
    print("\n📦 VERİ TOPLAMA BAŞLIYOR")
    print(f"   Hedef: {TARGET_GB} GB")
    print(f"   Kayıt klasörü: {RAW_DIR}\n")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total_bytes = 0

    active = sources or list(SOURCE_TARGETS.keys())

    if "knowledge" in active:
        print("\n[1/5] 📚 Bilgi Tabanı oluşturuluyor...")
        from collectors.web_scraper import collect as collect_knowledge
        n = collect_knowledge(RAW_DIR, SOURCE_TARGETS["knowledge"])
        _show_dir_size(RAW_DIR)

    if "wikipedia" in active:
        print("\n[2/5] 🌐 Wikipedia makaleleri toplanıyor...")
        from collectors.wikipedia_collector import collect as collect_wiki
        n = collect_wiki(RAW_DIR, SOURCE_TARGETS["wikipedia"])
        _show_dir_size(RAW_DIR)

    if "arxiv" in active:
        print("\n[3/5] 📄 arXiv makaleleri toplanıyor...")
        from collectors.arxiv_collector import collect as collect_arxiv
        n = collect_arxiv(RAW_DIR, SOURCE_TARGETS["arxiv"])
        _show_dir_size(RAW_DIR)

    if "github" in active:
        print("\n[4/5] 💻 GitHub repo'ları toplanıyor...")
        print("   (GITHUB_TOKEN env varı yoksa hız sınırlı)")
        from collectors.github_collector import collect as collect_github
        n = collect_github(RAW_DIR, SOURCE_TARGETS["github"])
        _show_dir_size(RAW_DIR)

    if "finance" in active:
        print("\n[5/5] 💰 Finans/Kripto verileri toplanıyor...")
        from collectors.finance_collector import collect as collect_finance
        n = collect_finance(RAW_DIR, SOURCE_TARGETS["finance"])
        _show_dir_size(RAW_DIR)

    total = sum(f.stat().st_size for f in RAW_DIR.glob("*.jsonl"))
    print(f"\n✅ TOPLAM VERİ: {total/1e9:.2f} GB ({total/1e6:.0f} MB)")
    return total


def process_data():
    """Ham veriyi eğitime hazırla."""
    print("\n🔄 VERİ İŞLENİYOR...")
    from processor import process_all, split_train_val
    stats = process_all(RAW_DIR, PROCESSED_DIR, mode="instruct")
    print("\n✂️ Train/Val bölünüyor...")
    split_train_val(PROCESSED_DIR)
    return stats


def train_model(quick: bool = False):
    """Modeli eğit."""
    print("\n🧠 MODEL EĞİTİMİ BAŞLIYOR...")
    from train import TrainConfig, train
    config = TrainConfig()
    if quick:
        config.num_epochs = 1
        config.max_samples = 5000
        print("  ⚡ Hızlı mod: 1 epoch, 5000 örnek")
    train(config)


def status():
    """Mevcut durum raporu."""
    print(BANNER)
    print("📊 DURUM RAPORU")
    print("─" * 50)

    # Ham veri
    raw_total = sum(f.stat().st_size for f in RAW_DIR.glob("*.jsonl")) if RAW_DIR.exists() else 0
    print(f"\n📁 Ham Veri: {raw_total/1e6:.1f} MB / {TARGET_GB*1000:.0f} MB hedef")
    if RAW_DIR.exists():
        for f in sorted(RAW_DIR.glob("*.jsonl")):
            size = f.stat().st_size
            count = sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))
            print(f"   {f.name:30s} {size/1e6:8.1f} MB  ({count:,} kayıt)")

    # İşlenmiş veri
    proc_total = sum(f.stat().st_size for f in PROCESSED_DIR.glob("*.jsonl")) if PROCESSED_DIR.exists() else 0
    print(f"\n⚙️  İşlenmiş Veri: {proc_total/1e6:.1f} MB")

    # Model
    model_dir = BASE_DIR / "models" / "semihcim4.0"
    if model_dir.exists():
        model_size = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
        print(f"\n🤖 Model: {model_size/1e6:.1f} MB — {model_dir}")
    else:
        print("\n🤖 Model: Henüz eğitilmedi")

    print("\n─" * 50)
    print("Kullanım:")
    print("  python main.py --collect       → Veri topla")
    print("  python main.py --process       → Veriyi işle")
    print("  python main.py --train         → Modeli eğit")
    print("  python main.py --train --quick → Hızlı test eğitimi")
    print("  python main.py --all           → Her şeyi yap")
    print("  python main.py --chat          → Model ile sohbet")


def _show_dir_size(d: Path):
    total = sum(f.stat().st_size for f in d.glob("*.jsonl"))
    print(f"   📁 Toplam veri: {total/1e6:.1f} MB")


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="semihcim4.0 AI Eğitim Sistemi")
    parser.add_argument("--collect", action="store_true", help="Veri topla")
    parser.add_argument("--source", nargs="+",
                        choices=["wikipedia", "arxiv", "github", "finance", "knowledge"],
                        help="Sadece belirli kaynaklar")
    parser.add_argument("--process", action="store_true", help="Veriyi işle")
    parser.add_argument("--train", action="store_true", help="Modeli eğit")
    parser.add_argument("--quick", action="store_true", help="Hızlı test modu")
    parser.add_argument("--all", action="store_true", help="Tüm adımları çalıştır")
    parser.add_argument("--status", action="store_true", help="Durum raporu")
    parser.add_argument("--chat", action="store_true", help="Yerel model ile sohbet")
    args = parser.parse_args()

    if args.status or len(sys.argv) == 1:
        status()
        return

    if args.all:
        collect_all()
        process_data()
        train_model(quick=args.quick)
        return

    if args.collect:
        collect_all(sources=args.source)

    if args.process:
        process_data()

    if args.train:
        train_model(quick=args.quick)

    if args.chat:
        from train import chat_inference
        model_path = str(BASE_DIR / "models" / "semihcim4.0")
        print("\nsemihcim4.0 Yerel Model Sohbet (Ctrl+C çıkış)")
        print("─" * 40)
        while True:
            try:
                q = input("\nSen: ").strip()
                if not q:
                    continue
                print("\nsemihcim4.0:", chat_inference(model_path, q))
            except KeyboardInterrupt:
                print("\nGüle güle!")
                break


if __name__ == "__main__":
    main()
