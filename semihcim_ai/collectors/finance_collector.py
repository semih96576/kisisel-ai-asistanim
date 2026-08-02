"""
Finans ve Kripto veri toplayıcı — Ücretsiz API'lar
"""
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

COINGECKO_API = "https://api.coingecko.com/api/v3"
ALPHAVANTAGE_API = "https://www.alphavantage.co/query"

TOP_CRYPTOS = [
    "bitcoin", "ethereum", "binancecoin", "solana", "cardano",
    "polkadot", "avalanche-2", "chainlink", "polygon", "uniswap",
    "litecoin", "bitcoin-cash", "stellar", "dogecoin", "shiba-inu",
    "cosmos", "algorand", "vechain", "filecoin", "tron",
    "aave", "compound-governance-token", "maker", "curve-dao-token",
    "yearn-finance", "synthetix-network-token", "1inch", "pancakeswap-token",
]

INVESTOPEDIA_ARTICLES = [
    "https://www.investopedia.com/terms/t/technicalanalysis.asp",
    "https://www.investopedia.com/terms/f/fundamentalanalysis.asp",
    "https://www.investopedia.com/terms/p/portfolio.asp",
    "https://www.investopedia.com/terms/d/diversification.asp",
    "https://www.investopedia.com/terms/r/riskmanagement.asp",
    "https://www.investopedia.com/terms/b/bitcoin.asp",
    "https://www.investopedia.com/terms/b/blockchain.asp",
    "https://www.investopedia.com/terms/d/defi.asp",
    "https://www.investopedia.com/terms/c/cryptocurrency.asp",
    "https://www.investopedia.com/terms/s/stockmarket.asp",
]

CRYPTO_EDUCATION = {
    "bitcoin": {
        "title": "Bitcoin — Kapsamlı Rehber",
        "text": """Bitcoin (BTC), 2009 yılında Satoshi Nakamoto takma adlı kişi veya grup tarafından
        oluşturulan ilk merkezi olmayan dijital para birimidir.

        TEMEL ÖZELLİKLER:
        - Maksimum arz: 21 milyon BTC
        - Konsensüs: Proof of Work (PoW)
        - Blok süresi: ~10 dakika
        - Halving: Her 210.000 blokta bir
        - Mining algoritması: SHA-256

        BLOCKCHAIN YAPISI:
        Bitcoin blockchain'i, her bloğun önceki bloğun hash'ini içerdiği zincirleme bloklar
        sistemine dayanır. Her blok: başlık (header), işlemler (transactions), Merkle tree kökü içerir.

        MADENCILIK (MINING):
        Madenciler, belirli sayıda sıfırla başlayan hash bulmak için nonce değerini değiştirir.
        Difficulty her 2016 blokta (yaklaşık 2 haftada) yeniden ayarlanır.
        Hash rate arttıkça difficulty artar.

        WALLET TÜRLERİ:
        - Hot wallet: İnternete bağlı (daha az güvenli)
        - Cold wallet: Çevrimdışı (hardware wallet, paper wallet)
        - Custodial: Borsa tutar (Coinbase, Binance)
        - Non-custodial: Kullanıcı private key'i tutar

        TEKNİK ANALİZ:
        Bitcoin fiyat analizi için kullanılan başlıca göstergeler:
        - Moving Average (MA, EMA): Trend yönü
        - RSI (Relative Strength Index): 0-100, aşırı alım/satım
        - MACD: Momentum göstergesi
        - Bollinger Bands: Volatilite göstergesi
        - Volume: İşlem hacmi
        - On-chain metrics: Active addresses, NVT ratio, SOPR

        HALVING ETKİSİ:
        2012: 50→25 BTC/blok | 2016: 25→12.5 | 2020: 12.5→6.25 | 2024: 6.25→3.125
        Tarihsel olarak halving'den 12-18 ay sonra ATH görülmüştür.

        LAYER 2 ÇÖZÜMLER:
        Lightning Network: Mikro ödemeler için off-chain ödeme kanalları
        Liquid Network: Hızlı işlemler için sidechain
        RGB Protocol: Bitcoin üzerinde akıllı sözleşmeler""",
    },
    "ethereum": {
        "title": "Ethereum — Kapsamlı Rehber",
        "text": """Ethereum (ETH), 2015'te Vitalik Buterin tarafından başlatılan,
        Turing-complete akıllı sözleşme platformudur.

        TEMEL ÖZELLİKLER:
        - Konsensüs: Proof of Stake (The Merge, 2022)
        - Blok süresi: ~12 saniye
        - EVM (Ethereum Virtual Machine)
        - Gas mekanizması: EIP-1559 (base fee + tip)
        - Staking: Min 32 ETH validator için

        AKILLI SÖZLEŞMELER:
        Solidity ile yazılır, EVM bytecode'a derlenir.
        Özellikler: immutable (değiştirilemez), transparent, trustless

        DeFi EKOSİSTEMİ:
        - DEX: Uniswap (AMM), Curve, SushiSwap
        - Lending: Aave, Compound, MakerDAO
        - Yield: Yearn Finance, Convex
        - Derivatives: dYdX, Synthetix
        - Insurance: Nexus Mutual

        LAYER 2 ÇÖZÜMLER:
        Optimistic Rollups: Arbitrum, Optimism (fraud proofs)
        ZK-Rollups: StarkNet, zkSync, Polygon zkEVM (validity proofs)
        State Channels, Sidechains: Polygon PoS

        TOKEN STANDARTLARI:
        - ERC-20: Fungible token (değiştirilebilir)
        - ERC-721: NFT (tekil)
        - ERC-1155: Multi-token
        - ERC-4626: Vault standardı

        GAS OPTİMİZASYON:
        - Storage SLOAD/SSTORE en pahalı
        - Events emit yerine storage tercih
        - Assembly kullanımı (inline)
        - Calldata vs memory
        - Batch işlemler""",
    },
}

FINANCE_EDUCATION = {
    "teknik_analiz": {
        "title": "Teknik Analiz — Kapsamlı Rehber",
        "text": """Teknik analiz, geçmiş fiyat ve hacim verilerini kullanarak
        gelecekteki fiyat hareketlerini tahmin etme metodolojisidir.

        TEMEL İLKELER:
        1. Piyasa her şeyi fiyatlar (Price discounts everything)
        2. Fiyatlar trend içinde hareket eder
        3. Tarih tekerrür eder

        TREND ANALİZİ:
        - Uptrend: Higher highs + higher lows
        - Downtrend: Lower highs + lower lows
        - Sideways: Range-bound
        - Trendline: Destek/Direnç çizgileri

        HAREKETL ORTALAMALAR:
        Simple MA (SMA): (P1+P2+...+Pn)/n
        Exponential MA (EMA): Ağırlıklı, son fiyatlara daha fazla ağırlık
        Golden Cross: 50-MA, 200-MA yukarı keser → Bullish
        Death Cross: 50-MA, 200-MA aşağı keser → Bearish

        OSİLATÖRLER:
        RSI (Relative Strength Index):
          RSI = 100 - (100 / (1 + RS))
          RS = Ortalama kazanç / Ortalama kayıp (14 periyot)
          >70: Aşırı alım | <30: Aşırı satım

        MACD (Moving Average Convergence Divergence):
          MACD Line = EMA(12) - EMA(26)
          Signal Line = EMA(9) of MACD
          Histogram = MACD - Signal

        Stochastic Oscillator:
          %K = (Close - Lowest Low) / (Highest High - Lowest Low) × 100

        FORMASYONLAR:
        Dönüş formasyonları:
        - Head and Shoulders (Baş ve Omuzlar)
        - Double Top/Bottom (Çift Tepe/Dip)
        - Triple Top/Bottom
        Devam formasyonları:
        - Flag (Bayrak)
        - Pennant (Flama)
        - Triangle (Üçgen): Ascending, Descending, Symmetrical
        - Cup and Handle

        MUM GRAFİKLERİ (CANDLESTICK):
        - Doji: Kararsızlık
        - Hammer/Hanging Man: Dönüş sinyali
        - Engulfing: Güçlü dönüş
        - Morning/Evening Star: 3 mum formasyon

        FIBONACCI DÜZELTMELERİ:
        Temel seviyeler: 23.6%, 38.2%, 50%, 61.8%, 78.6%
        Uzatma seviyeleri: 127.2%, 161.8%, 261.8%

        HACIM ANALİZİ:
        OBV (On-Balance Volume): Trend onayı
        Volume Profile: Fiyat seviyelerinde hacim dağılımı
        VWAP: Volume Weighted Average Price""",
    },
    "risk_yonetimi": {
        "title": "Risk Yönetimi — Finansal Rehber",
        "text": """Risk yönetimi, yatırım portföyündeki potansiyel kayıpları minimize etme
        ve getiriyi optimize etme sürecidir.

        TEMEL KAVRAMLAR:
        1. Risk/Reward oranı: Minimum 1:2 hedeflenmeli
        2. Position sizing: Her işlemde max %1-2 risk
        3. Stop-loss: Önceden belirlenen zarar kesme noktası
        4. Take-profit: Kar realizasyon hedefi

        PORTFÖY TEORİSİ:
        Modern Portföy Teorisi (Markowitz):
        - Diversification: Korelasyonsuz varlıklar
        - Efficient Frontier: Optimal risk/getiri
        - Sharpe Ratio = (Rp - Rf) / σp
          Rp: Portföy getirisi, Rf: Risksiz faiz, σp: Standart sapma

        VAR (VALUE AT RISK):
        Belirli güven aralığında maksimum beklenen kayıp
        Örnek: %95 VaR = 10.000 TL → %5 ihtimalle 10.000 TL'den fazla kayıp

        BETA KATSAYISI:
        β < 1: Piyasadan az volatil
        β = 1: Piyasa ile aynı
        β > 1: Piyasadan fazla volatil
        β < 0: Piyasa ile ters hareket

        KRİPTO RİSK YÖNETİMİ:
        - Maksimum drawdown takibi
        - Kaldıraç kullanımında dikkat (liquidation riski)
        - Likidite riski (düşük hacimli coinler)
        - Akıllı sözleşme riski (audit edilmemiş protokoller)
        - Exchange riski (merkezi borsa iflası)

        STOP-LOSS STRATEJİLERİ:
        - Sabit yüzde: %5-10
        - ATR tabanlı: 1.5-2x ATR
        - Destek/Direnç tabanlı
        - Trailing stop: Karı koru""",
    },
}


def fetch_crypto_data(output_dir: Path) -> int:
    """CoinGecko ücretsiz API'dan kripto verileri çek."""
    out_file = output_dir / "crypto_market.jsonl"
    count = 0

    with open(out_file, "a", encoding="utf-8") as f:
        # Eğitim içerikleri
        for key, content in CRYPTO_EDUCATION.items():
            record = {
                "title": content["title"],
                "text": content["text"],
                "category": "kripto",
                "domain": "education",
                "source": "semihcim4.0-knowledge-base",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

        for key, content in FINANCE_EDUCATION.items():
            record = {
                "title": content["title"],
                "text": content["text"],
                "category": "finans",
                "domain": "education",
                "source": "semihcim4.0-knowledge-base",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

        # CoinGecko'dan kripto bilgileri
        print("  CoinGecko'dan kripto verileri çekiliyor...")
        for crypto_id in TOP_CRYPTOS[:20]:
            try:
                r = requests.get(
                    f"{COINGECKO_API}/coins/{crypto_id}",
                    params={"localization": False, "tickers": False,
                            "market_data": True, "community_data": False,
                            "developer_data": False},
                    timeout=15,
                    headers={"User-Agent": "semihcim4.0-datacollector/1.0"}
                )
                if r.status_code == 429:
                    print("  Rate limit, 60s bekleniyor...")
                    time.sleep(60)
                    continue
                r.raise_for_status()
                data = r.json()

                desc = data.get("description", {}).get("en", "")
                market = data.get("market_data", {})
                record = {
                    "title": f"{data.get('name')} ({data.get('symbol', '').upper()}) — Kripto Bilgisi",
                    "text": f"""Kripto Para: {data.get('name')} ({data.get('symbol', '').upper()})

Açıklama: {desc[:3000] if desc else 'Açıklama yok'}

Piyasa Verileri:
- Piyasa Değeri Sıralaması: #{market.get('market_cap_rank', 'N/A')}
- Mevcut Fiyat (USD): ${market.get('current_price', {}).get('usd', 'N/A')}
- Piyasa Değeri (USD): ${market.get('market_cap', {}).get('usd', 'N/A')}
- 24s Hacim: ${market.get('total_volume', {}).get('usd', 'N/A')}
- Toplam Arz: {market.get('total_supply', 'N/A')}
- Dolaşımdaki Arz: {market.get('circulating_supply', 'N/A')}

Kategoriler: {', '.join(data.get('categories', [])[:10])}
Blockchain/Platform: {data.get('asset_platform_id', 'standalone')}
Genesis Tarihi: {data.get('genesis_date', 'N/A')}""",
                    "coin_id": crypto_id,
                    "symbol": data.get("symbol", ""),
                    "category": "kripto",
                    "domain": "coingecko",
                    "source": f"https://www.coingecko.com/en/coins/{crypto_id}",
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
                print(f"  ✓ {data.get('name')}")
                time.sleep(1.5)
            except Exception as e:
                print(f"  [HATA] {crypto_id}: {e}")
                time.sleep(2)

    return count


def collect(output_dir: Path, target_gb: float = 0.5) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    count = fetch_crypto_data(output_dir)
    print(f"\n  ✅ Finans/Kripto: {count} kayıt")
    return count
