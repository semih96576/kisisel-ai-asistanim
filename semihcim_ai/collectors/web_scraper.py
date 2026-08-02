"""
Genel web scraper — Teknik dökümanlar, forumlar, eğitim siteleri
"""
import time
import json
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

SOURCES = {
    "elektronik": [
        "https://www.electronicshub.org/",
        "https://circuitdigest.com/",
        "https://www.electronics-tutorials.ws/",
        "https://www.allaboutcircuits.com/",
    ],
    "yazilim": [
        "https://realpython.com/",
        "https://www.geeksforgeeks.org/",
        "https://towardsdatascience.com/",
    ],
    "finans_kripto": [
        "https://www.investopedia.com/",
        "https://academy.binance.com/en",
        "https://ethereum.org/en/developers/docs/",
    ],
}

# Doğrudan içerik üretimi — kendi bilgi tabanı
KNOWLEDGE_BASE = [
    # === ELEKTRONİK / ELEKTRİK ===
    {
        "title": "Temel Elektronik Devre Analizi",
        "category": "elektronik",
        "text": """ELEKTRONİK DEVRE ANALİZİ KAPSAMLI REHBERİ

OHM KANUNU:
V = I × R
Gerilim (V) = Akım (I) × Direnç (R)
Güç: P = V × I = I²R = V²/R

KİRCHHOFF KANUNLARI:
KCL (Akım): Bir düğüme giren akımların toplamı = Çıkan akımların toplamı
KVL (Gerilim): Kapalı bir çevrimde gerilim düşümlerinin cebirsel toplamı = 0

DİRENÇ BAĞLANTILARI:
Seri: R_toplam = R1 + R2 + R3 + ...
Paralel: 1/R_toplam = 1/R1 + 1/R2 + 1/R3 + ...

KONDÜKTİF DEVRE ELEMANLARI:
Kapasitör:
  Q = C × V
  Enerji: E = (1/2) × C × V²
  İmpedans: Xc = 1/(2πfC)
  AC gerilimden 90° geri kalır

Bobin (İndüktör):
  V = L × (dI/dt)
  Enerji: E = (1/2) × L × I²
  İmpedans: XL = 2πfL
  AC gerilimden 90° ileridedir

RLC DEVRESİ:
Rezonans frekansı: f0 = 1/(2π√(LC))
Q faktörü: Q = (1/R)√(L/C)
Bant genişliği: BW = f0/Q

TRANSİSTÖR (BJT):
NPN: Küçük baz akımı, büyük kolektör akımı kontrol eder
β (hFE) = IC/IB (kazanç katsayısı, genellikle 100-300)
Çalışma bölgeleri: Aktif, Doyum (Saturation), Kesim (Cutoff)
Uygulamalar: Amplifier, Switch, Oscillator

MOSFET:
N-MOSFET: Gate pozitif → Kanal oluşur → Drain-Source arası iletken
P-MOSFET: Gate negatif → Kanal oluşur
Eşik gerilimi (Vth), Transconductance (gm)
Uygulamalar: Power switching, Amplifiers, Digital logic

OP-AMP (İşlemsel Yükselteç):
İdeal op-amp: Sonsuz kazanç, sonsuz giriş empedansı, sıfır çıkış empedansı
Inverting: Av = -Rf/Rin
Non-inverting: Av = 1 + Rf/Rin
Summing amplifier, Differentiator, Integrator, Comparator

GÜNEŞ PANELİ (SOLAR CELL):
Tek diyot modeli: I = Iph - I0(e^(qV/nkT) - 1)
MPP (Maximum Power Point) tracking: MPPT algoritmaları
Dizi bağlantı: Seri → Gerilim artar, Paralel → Akım artar

MOTOR SÜRÜCÜLERİ:
DC Motor: PWM ile hız kontrolü, H-Bridge devresi
Stepper Motor: Step/Dir sinyali, mikrostep
BLDC: Sensörlü/sensörsüz, FOC (Field Oriented Control)
Servo: Kapalı döngü pozisyon kontrolü""",
    },
    {
        "title": "Gömülü Sistemler ve Mikrodenetleyiciler",
        "category": "elektronik",
        "text": """GÖMÜLü SİSTEMLER KAPSAMLI REHBERİ

MİKRODENETLEYİCİ MİMARİLERİ:
Harvard Mimarisi: Program ve veri belleği ayrı (PIC, AVR)
Von Neumann: Program ve veri belleği ortak (ARM Cortex-M)
RISC vs CISC: Komut seti karmaşıklığı

ARM CORTEX-M SERİSİ:
Cortex-M0/M0+: Ultra düşük güç, temel işlemler
Cortex-M3: Daha fazla komut seti
Cortex-M4: DSP komutları, FPU (Floating Point Unit)
Cortex-M7: Yüksek performans, çift hassasiyet FPU
Cortex-M33/M55: TrustZone güvenlik

STM32 AİLESİ:
STM32F103 (Blue Pill): 72MHz, 128KB Flash, 20KB RAM
STM32F407: 168MHz, 1MB Flash, 192KB RAM
STM32H743: 480MHz, 2MB Flash, 1MB RAM
HAL (Hardware Abstraction Layer) kütüphanesi
CubeMX: Grafik konfigürasyon aracı

ARDUINO PROGRAMLAMA:
setup() - Bir kez çalışır
loop() - Sürekli döngü
Digital I/O: pinMode(), digitalWrite(), digitalRead()
Analog I/O: analogRead() (10-bit, 0-1023), analogWrite() (PWM)
Serial: Serial.begin(9600), Serial.print(), Serial.read()
Interrupt: attachInterrupt(pin, ISR, mode)
Timers: millis(), micros(), delay()

İLETİŞİM PROTOKOLLERİ:
UART (Serial):
  Asenkron, TX/RX
  Baud rate: 9600, 115200, vb.
  Parite, stop bit ayarları

I2C (TWI):
  2 hat: SDA (veri), SCL (saat)
  Master-Slave
  7-bit/10-bit adres
  400kHz (Fast), 1MHz (Fast+), 3.4MHz (High Speed)
  Sensörler: MPU6050, BMP280, SSD1306

SPI:
  4 hat: MOSI, MISO, SCK, CS
  Full-duplex
  Hız: 10MHz'e kadar
  Kullanım: SD kart, TFT ekran, ADC/DAC

RTOS (Gerçek Zamanlı OS):
FreeRTOS: En yaygın, açık kaynak
Task oluşturma, semaphore, mutex, queue
Zaman dilimi (time slice), preemptive scheduling

INTERRUPT VE TIMER:
External interrupt: EXTI, edge/level tetikleme
Timer interrupt: Overflow, Compare, PWM üretimi
DMA (Direct Memory Access): CPU'suz bellek aktarımı""",
    },
    # === YAZILIM ===
    {
        "title": "Python Programlama — İleri Seviye",
        "category": "yazilim",
        "text": """PYTHON İLERİ SEVİYE PROGRAMLAMA REHBERİ

VERİ YAPILARI VE PERFORMANS:
List vs Tuple vs Set vs Dict:
  List: O(1) index erişim, O(n) arama
  Dict: O(1) ortalama arama, hash tablosu
  Set: O(1) üyelik testi
  deque (collections): O(1) her iki uçtan ekleme/silme

GENERATOR VE ITERATOR:
  def fibonacci():
      a, b = 0, 1
      while True:
          yield a
          a, b = b, a + b

  # Generator expression (lazy evaluation)
  squares = (x**2 for x in range(1000000))  # Bellek verimli

DECORATORS:
  import functools
  def timer(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
          import time
          start = time.perf_counter()
          result = func(*args, **kwargs)
          print(f"{func.__name__}: {time.perf_counter()-start:.4f}s")
          return result
      return wrapper

CONTEXT MANAGERS:
  class DatabaseConnection:
      def __enter__(self): return self.connect()
      def __exit__(self, *args): self.disconnect()

  with DatabaseConnection() as db:
      db.query("SELECT * FROM users")

ASYNC/AWAIT (ASYNCIO):
  import asyncio

  async def fetch_data(url):
      async with aiohttp.ClientSession() as session:
          async with session.get(url) as resp:
              return await resp.json()

  async def main():
      tasks = [fetch_data(url) for url in urls]
      results = await asyncio.gather(*tasks)

METACLASS:
  class Singleton(type):
      _instances = {}
      def __call__(cls, *args, **kwargs):
          if cls not in cls._instances:
              cls._instances[cls] = super().__call__(*args, **kwargs)
          return cls._instances[cls]

NUMPY/PANDAS OPTİMİZASYON:
  # Vectorized operations (C hızında)
  import numpy as np
  arr = np.array([1, 2, 3, 4, 5])
  result = arr * 2 + 1  # Element-wise, döngüsüz

  # Pandas chaining
  df = (pd.read_csv('data.csv')
        .dropna()
        .rename(columns={'old': 'new'})
        .assign(ratio=lambda x: x['a'] / x['b'])
        .query('ratio > 1'))

MULTIPROCESSING VS THREADING:
  GIL (Global Interpreter Lock): Python thread'leri CPU'yu tam kullanamaz
  Threading: I/O bound işlemler (ağ, dosya)
  Multiprocessing: CPU bound işlemler (hesaplama)

  from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
  with ProcessPoolExecutor() as executor:
      results = list(executor.map(process_chunk, data_chunks))

MEMORY PROFILING:
  from memory_profiler import profile
  @profile
  def memory_intensive(): ...

  # tracemalloc
  import tracemalloc
  tracemalloc.start()
  # ... kod ...
  snapshot = tracemalloc.take_snapshot()""",
    },
    {
        "title": "Machine Learning — Derin Öğrenme Temelleri",
        "category": "yazilim",
        "text": """MAKİNE ÖĞRENMESİ VE DERİN ÖĞRENME REHBERİ

TEMEL ML KATEGORİLERİ:
1. Supervised Learning: Etiketli veri
   - Regression: Sayısal tahmin
   - Classification: Kategori tahmini
2. Unsupervised Learning: Etiketsiz veri
   - Clustering: K-Means, DBSCAN, Hierarchical
   - Dimensionality Reduction: PCA, t-SNE, UMAP
3. Reinforcement Learning: Ödül/ceza tabanlı öğrenme

TEMEL ALGORİTMALAR:
Linear Regression: ŷ = β0 + β1x1 + ... + βnxn
  MSE Loss: L = (1/n)Σ(yi - ŷi)²
  Gradient Descent: β := β - α × ∂L/∂β

Logistic Regression:
  σ(z) = 1/(1 + e^(-z))
  Binary cross-entropy loss

Decision Tree:
  Gini impurity: 1 - Σ(pi²)
  Information gain: H(parent) - Σ(H(child))

Random Forest: N ağaç, bootstrap sampling, feature bagging
Gradient Boosting (XGBoost, LightGBM): Sequential ensemble

YAPAY SİNİR AĞLARI:
Perceptron: y = f(Σ(wi×xi) + b)
Aktivasyon fonksiyonları:
  ReLU: max(0, x) — En yaygın
  Sigmoid: 1/(1+e^(-x)) — Binary output
  Tanh: (e^x - e^(-x))/(e^x + e^(-x)) — Gizli katman
  Softmax: e^xi / Σ(e^xj) — Multi-class output
  GELU, SiLU: Modern modeller

BACKPROPAGATION:
∂L/∂wi = ∂L/∂ŷ × ∂ŷ/∂zi × ∂zi/∂wi
Chain rule ile katman katman gradient hesabı

OPTİMİZATÖRLER:
SGD: w := w - α × ∇L
Momentum: v := βv + α∇L; w := w - v
Adam: Adaptive moment estimation
  m := β1×m + (1-β1)×∇L
  v := β2×v + (1-β2)×(∇L)²
  w := w - α×m_hat/√(v_hat + ε)

CNN (KONVOLÜSYONEL AĞ):
Convolution: Feature extraction
Pooling: Boyut azaltma (Max, Average)
Batch Normalization: Eğitimi hızlandırır
Dropout: Aşırı öğrenmeyi önler
Mimariler: VGG, ResNet, EfficientNet, YOLO

TRANSFORMER MİMARİSİ:
Self-Attention: Q, K, V matrisleri
Attention(Q,K,V) = softmax(QK^T/√dk) × V
Multi-Head Attention: Paralel attention başları
Positional Encoding: sin/cos fonksiyonları
Feed-Forward Network, Layer Normalization
Encoder (BERT, ViT) vs Decoder (GPT) vs Encoder-Decoder (T5)

BÜYÜK DİL MODELLERİ (LLM):
GPT-3/4: Autoregressive, causal masking
BERT: Bidirectional, MLM (Masked Language Modeling)
LLaMA, Mistral, Phi: Açık kaynak modeller
Fine-tuning: LoRA, QLoRA, Full fine-tuning
RLHF: Reinforcement Learning from Human Feedback""",
    },
    # === FİNANS ===
    {
        "title": "Algoritmik Trading — Kapsamlı Rehber",
        "category": "finans",
        "text": """ALGORİTMİK TRADİNG KAPSAMLI REHBERİ

TEMEL KAVRAMLAR:
Algoritma türleri:
  - Trend following: Trendi takip et
  - Mean reversion: Ortalamaya dönüş
  - Arbitrage: Fiyat farkından kâr
  - Market making: Spread'den kâr
  - Statistical arbitrage: İstatistiksel anormallikler

BACKTESTING:
Geçmiş veriyle strateji testi
Dikkat edilecekler:
  - Survivorship bias: Sadece hayatta kalan varlıklar
  - Lookahead bias: Gelecek veriyi kullanma
  - Overfitting: Geçmiş veriye aşırı uyum
  - Transaction costs: Komisyon, slippage

PYTHON İLE TRADİNG:
  import pandas as pd
  import numpy as np

  # SMA Crossover stratejisi
  def sma_crossover(df, short=20, long=50):
      df['SMA_short'] = df['close'].rolling(short).mean()
      df['SMA_long'] = df['close'].rolling(long).mean()
      df['signal'] = 0
      df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1
      df.loc[df['SMA_short'] < df['SMA_long'], 'signal'] = -1
      return df

  # RSI hesaplama
  def calculate_rsi(prices, period=14):
      delta = pd.Series(prices).diff()
      gain = (delta.where(delta > 0, 0)).rolling(period).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
      rs = gain / loss
      return 100 - (100 / (1 + rs))

  # Bollinger Bands
  def bollinger_bands(df, period=20, std=2):
      df['BB_mid'] = df['close'].rolling(period).mean()
      df['BB_std'] = df['close'].rolling(period).std()
      df['BB_upper'] = df['BB_mid'] + std * df['BB_std']
      df['BB_lower'] = df['BB_mid'] - std * df['BB_std']
      return df

PERFORMANS METRİKLERİ:
  - Sharpe Ratio: (Rp - Rf) / σp (>1 iyi, >2 çok iyi)
  - Sortino Ratio: Sadece downside volatility
  - Max Drawdown: En büyük zirve-dip farkı
  - Calmar Ratio: CAGR / Max Drawdown
  - Win Rate: Kazanan işlem yüzdesi
  - Profit Factor: Gross Profit / Gross Loss

CANLI TRADİNG:
  # Binance API örneği
  from binance.client import Client
  client = Client(api_key, api_secret)

  # Piyasa emirleri
  order = client.order_market_buy(symbol='BTCUSDT', quantity=0.001)

  # Limit emir
  order = client.order_limit_buy(
      symbol='ETHUSDT', quantity=0.1, price='3000.00')

  # WebSocket (gerçek zamanlı fiyat)
  from binance.websockets import BinanceSocketManager
  bm = BinanceSocketManager(client)
  conn_key = bm.start_symbol_ticker_socket('BTCUSDT', process_message)

PORTFÖY OPTİMİZASYON:
  from scipy.optimize import minimize
  import numpy as np

  def portfolio_optimize(returns, target_return=None):
      n = len(returns.columns)
      cov_matrix = returns.cov() * 252  # Yıllık

      def portfolio_variance(weights):
          return weights.T @ cov_matrix @ weights

      constraints = [{'type': 'eq', 'fun': lambda w: sum(w) - 1}]
      bounds = tuple((0, 1) for _ in range(n))
      result = minimize(portfolio_variance, np.ones(n)/n,
                       method='SLSQP', bounds=bounds, constraints=constraints)
      return result.x""",
    },
]


def collect(output_dir: Path, target_gb: float = 1.0) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "knowledge_base.jsonl"
    count = 0

    with open(out_file, "a", encoding="utf-8") as f:
        for item in KNOWLEDGE_BASE:
            record = {
                "title": item["title"],
                "text": item["text"],
                "category": item["category"],
                "domain": "knowledge_base",
                "source": "semihcim4.0-curated",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            print(f"  ✓ {item['title']}")

    print(f"\n  ✅ Bilgi Tabanı: {count} kayıt")
    return count
