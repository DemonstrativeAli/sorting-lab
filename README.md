# Sorting Lab – Comparative Sorting Analysis

Sorting Lab; Quick, Heap, Shell, Merge ve Radix sort algoritmalarını GUI üzerinden deneyip, farklı veri setlerinde süre/bellek performanslarını ölçen, görselleştiren ve raporlayan kapsamlı bir analiz uygulamasıdır.

Bu README; kurulumdan kullanıma, modül mimarisinden fonksiyon referansına kadar uygulamanın tüm parçalarını detaylı şekilde açıklar. Ayrıca README odaklı bir Chatbot entegrasyonu içerir.

## İçindekiler

- [Özet](#özet)
- [Kurulum](#kurulum)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [GUI Ekranları](#gui-ekranları)
- [Veri Setleri ve Metrikler](#veri-setleri-ve-metrikler)
- [Algoritmalar](#algoritmalar)
- [Mimari ve Dosya Yapısı](#mimari-ve-dosya-yapısı)
- [Kütüphaneler ve Teknolojiler](#kütüphaneler-ve-teknolojiler)
- [Fonksiyon Referansı](#fonksiyon-referansı)
- [Bellek Yönetimi ve Profiling](#bellek-yönetimi-ve-profiling)
- [Performans Analizi](#performans-analizi)
- [C-Level Optimizasyonlar ve Python İç Yapısı](#c-level-optimizasyonlar-ve-python-iç-yapısı)
- [Teknik Dokümantasyon (Chatbot Bilgi Tabanı)](#teknik-dokümantasyon-chatbot-bilgi-tabanı)
- [Chatbot Entegrasyonu](#chatbot-entegrasyonu)
- [Testler](#testler)
- [Troubleshooting](#troubleshooting)

## Özet

- 5 farklı sıralama algoritmasını (Quick, Heap, Shell, Merge, Radix) hem tek deneme hem de karşılaştırmalı olarak çalıştırır.
- Farklı veri setlerinde (random, partial, reverse) zaman ve bellek metriklerini ölçer.
- Grafikler, tablolar ve canlı animasyonlarla sonuçları görselleştirir.
- README odaklı bir Chatbot ile uygulama içi yardım sağlar.

## Kurulum

1) Sanal ortam (opsiyonel):
```bash
python -m venv venv
source venv/bin/activate
```

2) Bağımlılıklar:
```bash
pip install -r requirements.txt
```

3) Paket kurulumu (önerilir):
```bash
pip install -e .
```

## Hızlı Başlangıç

GUI:
```bash
python -m sorting_lab.gui.app
```

CLI (toplu deney):
```bash
python -m sorting_lab.cli --algos quick,heap,merge --sizes 1000,10000 --dataset random --runs 3
```

## GUI Ekranları

### 1) Çalıştırma (Single Run)

- **Algoritma seçimi:** Tek algoritma seçilir.
- **Veri seti seçimi:** random / partial / reverse.
- **Boyut:** Seçilen veri seti büyüklüğü.
- **Çıktı önizleme:** İlk örnek elemanlar ve sıralı çıktı gösterilir.
- **Sonuç kartları:** Süre, ek bellek (peak delta) ve toplam bellek (peak RSS), dataset tipi, boyut gibi metrikler özetlenir.
- **Algoritma bilgisi:** Seçilen algoritmanın kısa açıklaması ve teorik best/worst bilgisi görünür.

### 2) Karşılaştırma (Compare)

- **Çoklu algoritma seçimi:** Birden fazla algoritma aynı koşullarda çalıştırılır.
- **Run sayısı:** Aynı senaryo birden fazla kez çalıştırılıp ortalama ve std sapma hesaplanır.
- **Performans tablosu:** Ortalama süre, std sapma, bellek kullanımı gösterilir.
- **Grafikler:** Bar/Line seçimi, metrik seçimi ve detaylı karşılaştırma grafiği.
- **Duraklatma:** Uzun işlemlerde durdurma butonu ile çalışmayı kesebilirsiniz.

### 3) Detaylı Karşılaştırma (Toplu)

- **Ayrı sayfa:** Karşılaştırma ekranının üstündeki **Detaylı Karşılaştırma** butonuyla ayrı bir sayfa olarak açılır.
- **Toplu test:** Random/partial/reverse veri setleri ve 1.000 / 10.000 / 100.000 boyutlarında tüm algoritmalar otomatik çalıştırılır.
- **Toplu grafikler:** Seçilen veri setleri için 1.000 / 10.000 / 100.000 boyutlarının grafikleri aynı ekranda gösterilir.
- **Tam tablo:** Tüm kombinasyonların sonuçları tek tabloda listelenir.

### 4) Adım Adım Görselleştirme (Live View)

- **Adım kaydı:** Algoritma, her adımda dizi durumunu kaydeder.
- **Canlı animasyon:** Sıralama süreci bar grafik olarak canlı izlenir.
- **FPS kontrolü:** Animasyon hızı FPS ile ayarlanır.
- **Adım limiti:** Büyük veri setlerinde performans için adım sayısı sınırlandırılır.

### 5) Chatbot

- **README tabanlı asistan:** Projenin kullanımını ve fonksiyonlarını README üzerinden açıklar.
- **OpenAI API entegrasyonu:** API key ile çalışır.
- **Butonlar:** Gönder, Temizle, README Yenile.

## Veri Setleri ve Metrikler

### Veri Setleri

- **random:** Rastgele sayılar.
- **partial:** Kısmen sıralı veri (kısmi düzen + karıştırma).
- **reverse:** Tersten sıralı veri.

### Metrikler

- **avg_time_s:** Çalışma süresinin ortalaması (saniye).
- **std_time_s:** Süre standart sapması.
- **memory_mb:** `tracemalloc` bazlı *ek bellek* (peak delta, MB). Algoritma sırasında yapılan Python bellek tahsislerinin tepe noktasıdır.
- **memory_peak_mb:** RSS bazlı *toplam peak bellek* (MB). Çalışma sırasında görülen maksimum süreç belleği.

## Algoritmalar

| Algoritma | Best | Avg | Worst | Ek Bellek |
|---|---|---|---|---|
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) (stack) |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) |
| Shell Sort | Gap'e bağlı | Gap'e bağlı | ~O(n²) | O(1) |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Radix Sort | O(d(n+k)) | O(d(n+k)) | O(d(n+k)) | O(n+k) |

Not: Radix sort yalnızca negatif olmayan tamsayılar için uygundur.

## Mimari ve Dosya Yapısı

```
sorting-lab/
├── src/sorting_lab/
│   ├── algorithms/        # Sıralama algoritmaları
│   ├── analysis/          # Toplu deney ve raporlama
│   ├── gui/               # PySide6 GUI
│   ├── utils/             # Veri üretimi, metrikler, yardımcılar
│   └── cli.py             # CLI arayüzü
├── data/results/          # Deney çıktıları
├── tests/                 # Birim testleri
└── README.md              # Proje dokümantasyonu
```

## Kütüphaneler ve Teknolojiler

### Core Python Libraries (Standart Kütüphane)

#### 1. **time** - Zaman Ölçümü
```python
import time
start = time.perf_counter()
# işlem
elapsed = time.perf_counter() - start
```
- **Kullanım Amacı:** Algoritma çalışma süresini mikrosaniye hassasiyetinde ölçmek.
- **Neden perf_counter():** Sistem saati değişikliklerinden (NTP sync) etkilenmez, monotonic bir clock sağlar.
- **Alternatifler:** `time.time()` (duvar saati, NTP'den etkilenir), `time.process_time()` (sadece CPU zamanı).

#### 2. **tracemalloc** - Python Bellek Profiling
```python
import tracemalloc
tracemalloc.start()
# işlem
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
```
- **Kullanım Amacı:** Python heap'te tahsis edilen belleğin anlık ve peak değerlerini ölçer.
- **Ölçüm Kapsamı:** Yalnızca Python'un `malloc()` ile ayırdığı belleği takip eder; işletim sistemi belleği (RSS) değil.
- **Performans Maliyeti:** ~10-30% overhead ekler, üretim kodunda varsayılan olarak kapalıdır.
- **Önemli:** `get_traced_memory()` iki değer döner: *current* (şu anki kullanım) ve *peak* (tepe noktası).

#### 3. **psutil** - Sistem ve Süreç Metrikleri
```python
import psutil
process = psutil.Process()
rss_before = process.memory_info().rss
# işlem
rss_after = process.memory_info().rss
```
- **Kullanım Amacı:** İşletim sistemi seviyesinde gerçek bellek kullanımını (RSS - Resident Set Size) ölçer.
- **RSS (Resident Set Size):** Sürecin RAM'de tuttuğu toplam bellek (code, data, heap, stack dahil).
- **VMS (Virtual Memory Size):** Sanal bellek alanı (swap dahil, fiziksel RAM'den daha büyük olabilir).
- **Fark:** `tracemalloc` Python heap'i, `psutil` tüm süreci ölçer.

#### 4. **cProfile** ve **pstats** - Code Profiling
```python
import cProfile
import pstats
profiler = cProfile.Profile()
profiler.enable()
# işlem
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # En yavaş 10 fonksiyon
```
- **Kullanım Amacı:** Hangi fonksiyonların en çok zaman harcadığını tespit etmek.
- **Metrikler:** `tottime` (fonksiyonun kendi süresi), `cumtime` (alt çağrılar dahil toplam).
- **Overhead:** ~10% performans kaybı, ama üretim profiling için kabul edilebilir.

### GUI Framework

#### 5. **PySide6** - Qt for Python
```python
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread, Signal
```
- **Kullanım Amacı:** Profesyonel desktop GUI uygulaması geliştirmek.
- **Qt Framework:** C++ ile yazılmış, endüstri standardı cross-platform GUI kütüphanesi.
- **PySide6 vs PyQt6:** PySide6, Qt Company'nin resmi Python binding'i (LGPL lisanslı); PyQt6 üçüncü parti (GPL/Commercial).
- **Signal-Slot Mekanizması:** Thread-safe GUI güncellemeleri için event-driven programlama modeli.
- **QThread:** Uzun süren işlemleri arka planda çalıştırır, GUI donmasını engeller.

### Data Analysis ve Visualization

#### 6. **pandas** - Veri Analizi
```python
import pandas as pd
df = pd.DataFrame({'Algorithm': [...], 'Time': [...]})
df.groupby('Algorithm')['Time'].mean()
```
- **Kullanım Amacı:** Deney sonuçlarını tablo formatında organize etmek, istatistiksel analiz yapmak.
- **DataFrame:** SQL tablolarına benzer, indeksleme ve gruplama işlemleri hızlıdır.
- **Projede Kullanımı:** Karşılaştırma sonuçlarını toplamak, ortalama/std sapma hesaplamak.

#### 7. **matplotlib** - Grafik Çizimi
```python
import matplotlib.pyplot as plt
plt.bar(['Quick', 'Merge'], [0.5, 0.7])
plt.xlabel('Algorithm')
plt.ylabel('Time (s)')
plt.show()
```
- **Kullanım Amacı:** Performans metriklerini görselleştirmek (bar, line, scatter plots).
- **Backend:** PySide6 ile entegrasyon için `matplotlib.use('QtAgg')` kullanılır.
- **FigureCanvas:** Qt widget olarak matplotlib grafiklerini GUI'ye gömer.

### AI Integration

#### 8. **openai** - OpenAI API Client
```python
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "..."}]
)
```
- **Kullanım Amacı:** README tabanlı chatbot için GPT API entegrasyonu.
- **Streaming:** `stream=True` ile cevapları kelime kelime almak mümkün.
- **Token Limiti:** GPT-4: 8k-32k context window; GPT-3.5-turbo: 4k-16k.

### Configuration ve Environment

#### 9. **python-dotenv** - Ortam Değişkenleri
```python
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```
- **Kullanım Amacı:** API key'leri ve yapılandırma değerlerini `.env` dosyasından yüklemek.
- **Güvenlik:** `.env` dosyası `.gitignore`'da olmalı, hassas bilgilerin commit'lenmesini engeller.

### Testing

#### 10. **pytest** - Test Framework
```python
def test_quick_sort():
    arr = [3, 1, 2]
    result = quick_sort.sort(arr.copy())
    assert result == [1, 2, 3]
```
- **Kullanım Amacı:** Algoritmaların doğruluğunu otomatik test etmek.
- **Fixtures:** Test verilerini paylaşmak için `@pytest.fixture` dekoratörü.
- **Parametrize:** `@pytest.mark.parametrize` ile aynı testi farklı veri setlerinde çalıştırmak.

## Fonksiyon Referansı

Aşağıdaki liste, proje içindeki fonksiyonların rolünü özetler. GUI tarafında birçok yardımcı metot bulunur; burada ana akış ve kritik metotlar listelenmiştir.

### `src/sorting_lab/algorithms`

#### Quick Sort
- `quick_sort._record_state(arr, steps)`: Adım kaydı için dizi kopyasını `steps` listesine ekler.
- `quick_sort.sort(arr, steps=None)`: Median-of-three pivot + iteratif quicksort. `steps` opsiyonel liste, her adımda dizi durumu kaydedilir.
- `quick_sort.median_of_three(arr, low, high)`: Pivot seçimi için `arr[low]`, `arr[mid]`, `arr[high]` arasından ortancayı bulur.
- `quick_sort.partition(arr, low, high)`: Pivot etrafında parçalama; küçükler sola, büyükler sağa.

#### Heap Sort
- `heap_sort._record_state(arr, steps)`: Adım kaydı.
- `heap_sort.sort(arr, steps=None)`: Heap tabanlı sıralama.
- `heap_sort.heapify(arr, n, i)`: `i` indeksinden başlayarak max-heap özelliğini sağlar.

#### Merge Sort
- `merge_sort._record_state(arr, steps)`: Adım kaydı.
- `merge_sort.sort(arr, steps=None)`: Merge sort ana fonksiyonu.
- `merge_sort.merge_sort(arr, l, r, steps)`: Recursive bölme mantığı.
- `merge_sort.merge(arr, l, m, r)`: İki sıralı alt diziyi birleştirir.

#### Shell Sort
- `shell_sort._record_state(arr, steps)`: Adım kaydı.
- `shell_sort.sort(arr, steps=None)`: Gap tabanlı insertion sort. Gap dizisi: `n/2, n/4, ..., 1`.

#### Radix Sort
- `radix_sort.sort(arr, steps=None)`: LSD (Least Significant Digit) radix sort ana fonksiyonu.
- `radix_sort.record(arr, steps)`: Yerel adım kaydı fonksiyonu.

#### Factory Functions
- `algorithms.run_algorithm(key, arr, steps=None)`: Algoritma key'i ile uygun fonksiyonu çağırır.
- `algorithms.available_algorithms()`: Kullanılabilir algoritmalar listesi (`["quick", "heap", ...]`).
- `algorithms.keys()`: Algoritma anahtarlarını döndürür.

### `src/sorting_lab/utils`

#### Data Generation
- `data_gen.random_array(size, low=0, high=100000)`: Rastgele tamsayı dizisi üretir.
- `data_gen.partially_sorted_array(size, sorted_ratio=0.7)`: Kısmi sıralı veri seti. `sorted_ratio` kadarı sıralı, geri kalanı karıştırılmış.
- `data_gen.reverse_sorted_array(size)`: Ters sıralı veri seti (büyükten küçüğe).
- `data_gen.generate(dataset_name, size)`: Dataset adına göre uygun veri üretir (`"random"`, `"partial"`, `"reverse"`).

#### Metrics ve Profiling
- `metrics.measure(algo_func, arr)`: Algoritmayı çalıştırır ve performans metriklerini döndürür.
  - **Dönen Değer:** `MeasureResult(elapsed_s, memory_mb, memory_peak_mb)`
    - `elapsed_s`: Çalışma süresi (saniye)
    - `memory_mb`: Python heap peak delta (tracemalloc)
    - `memory_peak_mb`: İşletim sistemi RSS peak (psutil)
- `metrics.run_trials(algo_func, arr, num_runs=5)`: Algoritmayı `num_runs` kez çalıştırır, ortalama ve standart sapma hesaplar.
  - **Dönen Değer:** `TrialStats(avg_time_s, std_time_s, avg_memory_mb, avg_memory_peak_mb)`
- `metrics.MeasureResult`: Dataclass, tek ölçüm sonucu modeli.
- `metrics.TrialStats`: Dataclass, çoklu deneme istatistiği modeli.

- `profiling.profile_func(func, *args, **kwargs)`: cProfile ile fonksiyon profiling yapar, sonuçları `pstats.Stats` objesi olarak döner.
- `visualizer.plot_runtime(results_df, output_path)`: Pandas DataFrame'den matplotlib ile basit runtime grafiği üretir.

### `src/sorting_lab/analysis`

- `runner.run_experiments(algos, sizes, dataset, runs, output_dir)`: Toplu deney çalıştırır, sonuçları CSV dosyasına yazar.
  - **Parametreler:**
    - `algos`: Algoritma listesi (`["quick", "merge"]`)
    - `sizes`: Veri boyutları listesi (`[1000, 10000]`)
    - `dataset`: Veri seti tipi (`"random"`, `"partial"`, `"reverse"`)
    - `runs`: Her senaryo için tekrar sayısı
    - `output_dir`: Çıktı dizini
- `report.generate_report(csv_path, output_html)`: CSV'den basit HTML rapor üretir (algoritma karşılaştırma tablosu).

### `src/sorting_lab/cli.py`

- `parse_args()`: argparse ile CLI argümanlarını okur (`--algos`, `--sizes`, `--dataset`, `--runs`).
- `main()`: CLI akışı, `run_experiments` çağırır ve sonuçları ekrana yazdırır.

### `src/sorting_lab/gui/app.py`

- `MainWindow`: Ana pencere sınıfı, QTabWidget ile 4 tab yönetimi (Single Run, Compare, Live View, Chatbot).
- `run()`: PySide6 QApplication'ı başlatır, MainWindow'u gösterir ve event loop'u çalıştırır.

### `src/sorting_lab/gui/screens/single_run.py`

- `SingleRunView`: Tek algoritma çalıştırma ekranı (QWidget).
- `_on_run()`: "Run" butonuna basıldığında çağrılır:
  1. Seçili algoritmayı ve veri seti tipini okur.
  2. Veriyi üretir (`data_gen.generate`).
  3. Algoritmayı çalıştırır (`metrics.measure`).
  4. Sonuçları UI kartlarına yazar.
- `_render_preview(input_data, output_data)`: Giriş/çıkış önizleme tablosu üretir (ilk 10 eleman).
- `_update_algo_info(algo_key)`: Seçili algoritmanın açıklamalarını ve Big-O notasyonunu gösterir.
- `_set_status(message, is_error=False)`: Durum etiketini günceller.
- `_pulse_status()`: Durum etiketini animasyonlu şekilde büyütüp küçültür (QPropertyAnimation).
- `_sync_card_heights()`: Sonuç kartlarının yüksekliklerini eşitler (görsel tutarlılık için).

### `src/sorting_lab/gui/screens/compare.py`

- `CompareWorker(QThread)`: Arka planda karşılaştırma çalıştırır.
  - `run()`: Seçili algoritmaları sırayla ölçer, her biri için `metrics.run_trials` çağırır, sonuçları pandas DataFrame olarak `results_ready` sinyali ile gönderir.
  - `stop()`: `_is_running` flag'ini False yapar, döngüyü durdurur.
- `CompareView`: Karşılaştırma UI ekranı.
  - `_on_compare()`: "Compare" butonuna basıldığında worker başlatır.
  - `_render_table(df)`: Sonuç DataFrame'ini QTableWidget'a doldurur (algoritma adı, ortalama süre, std sapma, bellek).
  - `_render_chart(df, metric, chart_type)`: Metrik ve grafik tipi seçimine göre matplotlib grafiği hazırlar.
  - `_start_animation()`: Grafik animasyonunu başlatır (FuncAnimation ile bar yüksekliklerini kademeli olarak artırır).
  - `_toggle_detail_chart()`: Detaylı grafiği göster/gizle (ikinci bir FigureCanvas açar).
  - `_reset_chart()`: Grafiği sıfırlar, yeni karşılaştırma için hazırlar.

### `src/sorting_lab/gui/screens/live_view.py`

- `ArrayCanvas(QWidget)`: Bar grafik çizimi için custom widget; `paintEvent` ile canlı render.
  - `set_data(data)`: Dizi verilerini alır, `update()` çağırarak yeniden çizim tetikler.
  - `paintEvent(event)`: QPainter ile her elemanı bar olarak çizer (yükseklik değere göre).
- `LiveView`: Adım adım görselleştirme ekranı.
  - `_on_run()`: Veriyi üretir, algoritmayı adım kaydı ile çalıştırır, QTimer ile animasyon başlatır.
  - `_advance()`: Her timer tick'inde bir adım ilerler, `ArrayCanvas.set_data` ile günceller.
  - `_on_stop()`: Animasyonu durdurur, timer'ı iptal eder.

### `src/sorting_lab/gui/screens/chatbot.py`

- `ChatWorker(QThread)`: OpenAI API çağrısını arka planda yapar.
  - `run()`: `openai.ChatCompletion.create` ile mesajları gönderir, yanıtı `response_ready` sinyali ile döner.
- `ChatbotView`: Chatbot UI.
  - `_load_readme()`: README.md dosyasını okur, içeriğini string olarak döner.
  - `_build_system_message()`: README'yi system prompt'a ekler (`"Sen bir Python sorting algoritmaları uzmanısın. README: ..."` formatında).
  - `_on_send()`: Kullanıcı mesajını alır, sohbet geçmişine ekler, worker başlatır.
  - `_on_response(reply)`: API yanıtını sohbet ekranına yazar (QTextEdit'e HTML olarak).
  - `_reload_readme()`: README'yi yeniden yükler, kullanıcıya bildirim gösterir.

## Bellek Yönetimi ve Profiling

### Python Bellek Modeli

Python, bellek yönetimini **Heap Memory** üzerinde gerçekleştirir. Her Python objesi (int, list, dict, vb.) heap'te bir bellek bloğu tahsis eder.

#### Bellek Katmanları

1. **OS Level (Operating System)**
   - İşletim sistemi, süreçlere fiziksel RAM'den sayfa (page) tahsis eder.
   - **RSS (Resident Set Size):** Sürecin RAM'de tuttuğu toplam bellek.
   - **VMS (Virtual Memory Size):** Sanal bellek (swap dahil).

2. **Python Memory Allocator (pymalloc)**
   - Python, kendi bellek havuzunu (memory pool) yönetir.
   - Küçük objeler (<512 bayt) için özel arena sistemi kullanır (fragmentasyonu azaltır).
   - Büyük objeler için doğrudan `malloc()` çağrısı yapar.

3. **Object Level (Reference Counting + GC)**
   - Python, **reference counting** (referans sayma) ile bellek geri kazanımı yapar.
   - Bir objeye hiç referans kalmadığında hemen serbest bırakılır.
   - **Cyclic Garbage Collector (GC):** Döngüsel referansları (A → B → A) tespit edip temizler.

#### Bellek Ölçüm Araçları

| Araç | Ölçtüğü Alan | Kullanım |
|------|-------------|----------|
| `tracemalloc` | Python heap (pymalloc) | `tracemalloc.start()` → işlem → `get_traced_memory()` |
| `psutil` | İşletim sistemi RSS | `process.memory_info().rss` |
| `memory_profiler` | Satır satır bellek artışı | `@profile` dekoratörü (üçüncü parti) |
| `guppy3` | Heap snapshot | `from guppy import hpy; h = hpy(); h.heap()` |

### Projede Bellek Profiling

`utils/metrics.py` içinde iki metrik ölçülür:

1. **Python Ek Bellek (tracemalloc peak delta)**
   - Algoritma başlamadan önce `tracemalloc.start()`.
   - Algoritma bittikten sonra `get_traced_memory()[1]` (peak değeri).
   - Bu, algoritmanın Python heap'te ne kadar bellek tahsis ettiğini gösterir.

2. **Toplam Peak Bellek (psutil RSS)**
   - Algoritma başlamadan önce `psutil.Process().memory_info().rss`.
   - Algoritma sırasında periyodik olarak RSS ölçülür (veya başlangıç/bitiş farkı alınır).
   - Bu, sürecin toplam bellek tüketimini gösterir.

#### Örnek Kod

```python
import tracemalloc
import psutil

def measure_algorithm(algo_func, data):
    # Bellek ölçümünü başlat
    tracemalloc.start()
    process = psutil.Process()
    rss_before = process.memory_info().rss
    
    # Algoritmayı çalıştır
    start_time = time.perf_counter()
    result = algo_func(data.copy())
    elapsed = time.perf_counter() - start_time
    
    # Bellek ölçümünü oku
    current, peak_python = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_after = process.memory_info().rss
    
    return {
        'time_s': elapsed,
        'python_peak_mb': peak_python / 1024 / 1024,
        'rss_delta_mb': (rss_after - rss_before) / 1024 / 1024
    }
```

### Bellek Optimizasyon Teknikleri

1. **In-Place Sorting (Yerinde Sıralama)**
   - Quick Sort, Heap Sort, Shell Sort in-place çalışır (yeni dizi tahsis etmez).
   - Merge Sort ve Radix Sort ek dizi gerektirir ($O(n)$ bellek).

2. **Generator Kullanımı**
   - Büyük veri setlerini tümüyle belleğe almak yerine, `yield` ile parça parça işlemek.
   - Örnek: `for item in generate_data(1000000)` yerine `yield item`.

3. **Garbage Collection Kontrolü**
   - `gc.collect()` ile manuel GC tetiklemek (ölçüm öncesi temiz durum sağlar).
   - `gc.disable()` ile ölçüm sırasında GC'yi kapatmak (daha kararlı metrikler).

4. **Object Pooling**
   - Sık kullanılan objeleri yeniden kullanmak (örneğin, geçici listeler için).

## Performans Analizi

### Performans Analizi Nedir?

Performans analizi, bir yazılımın **çalışma süresi**, **bellek kullanımı**, **CPU kullanımı**, ve **I/O işlemlerini** sistematik olarak ölçüp yorumlamaktır. Amaç, darboğazları (bottlenecks) tespit etmek ve optimize etmektir.

### Analiz Türleri

#### 1. **Time Profiling (Zaman Profillemesi)**

Hangi fonksiyonların en çok zaman harcadığını tespit etmek.

**Araçlar:**
- `cProfile`: Python standart kütüphanesinde, C implementasyonu (düşük overhead).
- `line_profiler`: Satır satır profiling (üçüncü parti, `@profile` dekoratörü).
- `py-spy`: Sampling profiler (çalışan sürece attach olur, overhead yok).

**Örnek: cProfile Kullanımı**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Test edilecek kod
quick_sort.sort([5, 2, 8, 1, 9] * 1000)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # En yavaş 10 fonksiyon
```

**Çıktı Yorumlama:**
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1000    0.125    0.000    0.456    0.000 quick_sort.py:15(partition)
      500    0.089    0.000    0.234    0.000 quick_sort.py:8(median_of_three)
```
- `tottime`: Fonksiyonun kendi içinde geçirdiği süre (alt çağrılar hariç).
- `cumtime`: Alt çağrılar dahil toplam süre.
- `ncalls`: Fonksiyonun çağrılma sayısı.

#### 2. **Memory Profiling (Bellek Profillemesi)**

Hangi kod parçalarının en çok bellek tahsis ettiğini tespit etmek.

**Araçlar:**
- `tracemalloc`: Python standart kütüphanesinde, snapshot karşılaştırması yapabilir.
- `memory_profiler`: Satır satır bellek artışı gösterir.
- `pympler`: Nesne boyutlarını ve leak'leri tespit eder.

**Örnek: tracemalloc Snapshot**

```python
import tracemalloc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# Bellek tüketen kod
data = [i for i in range(1000000)]

snapshot2 = tracemalloc.take_snapshot()
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

for stat in top_stats[:5]:
    print(stat)
```

**Çıktı:**
```
data_gen.py:15: size=7629 KiB (+7629 KiB), count=1000001 (+1000001)
```

#### 3. **CPU Profiling (İşlemci Kullanımı)**

Hangi kod bölümlerinin CPU'yu en çok meşgul ettiğini tespit etmek.

**Araçlar:**
- `py-spy`: Sampling profiler, flame graph oluşturur.
- `perf`: Linux sistem profiler (C seviyesi analiz).

**Örnek: py-spy Kullanımı**

```bash
pip install py-spy
py-spy record -o profile.svg -- python -m sorting_lab.cli --algos quick --sizes 100000
```

Çıktı: `profile.svg` flame graph (hangi fonksiyonların ne kadar CPU kullandığını gösterir).

#### 4. **I/O Profiling (Giriş/Çıkış Analizi)**

Disk okuma/yazma ve ağ isteklerinin performansını ölçmek.

**Araçlar:**
- `iotop`: Sistem seviyesinde I/O izleme.
- `strace`: Sistem çağrılarını takip eder (Linux).

Bu projede I/O yoğun değil, ama büyük veri setlerini dosyadan okuma/yazma durumunda önemli.

### Projede Performans Analizi

#### 1. **Karşılaştırmalı Analiz**

`analysis/runner.py` içinde `run_experiments` fonksiyonu:
- Farklı algoritmaları aynı veri setinde çalıştırır.
- Her algoritma için ortalama süre, std sapma, bellek kullanımı hesaplanır.
- Sonuçlar CSV'ye yazılır, matplotlib ile grafikleştirilir.

**Metrikler:**
- `avg_time_s`: Ortalama çalışma süresi.
- `std_time_s`: Standart sapma (tutarlılık göstergesi).
- `memory_mb`: Ortalama Python heap kullanımı.
- `memory_peak_mb`: Ortalama RSS peak.

#### 2. **Veri Seti Etkisi**

Farklı veri setlerinde (random, partial, reverse) algoritmaların davranışını analiz etmek:

- **Random Data:** En genel durum, ortalama karmaşıklık ($O(n \log n)$).
- **Partial Data:** Shell Sort avantajlı (insertion sort mantığı).
- **Reverse Data:** Quick Sort kötü pivot seçimi ile $O(n^2)$ olabilir.

#### 3. **Adım Adım Analiz**

`gui/screens/live_view.py` içinde adım kaydı:
- Her algoritma çalışırken dizi durumu `steps` listesine kaydedilir.
- Animasyon ile görsel olarak darboğazlar (örneğin, pivotun yanlış seçilmesi) tespit edilebilir.

### Performans Optimizasyon Stratejileri

1. **Algoritma Seçimi**
   - Veri setine göre en uygun algoritmayı kullanmak (örneğin, küçük veri setlerinde insertion sort, büyük veri setlerinde quick sort).

2. **Veri Yapısı Optimizasyonu**
   - Liste yerine array kullanımı (numpy arrays, C seviyesinde daha hızlı).
   - Hash tabloları (dict) yerine set kullanımı (arama işlemlerinde).

3. **Parallelization (Paralelleştirme)**
   - `multiprocessing` ile farklı algoritmaları paralel çalıştırmak.
   - Thread-safe veri yapıları kullanmak.

4. **Caching (Önbellekleme)**
   - Sık hesaplanan değerleri cache'lemek (`functools.lru_cache`).

5. **JIT Compilation (Tam Zamanında Derleme)**
   - `numba` ile Python fonksiyonlarını makine koduna derlemek.
   - `cython` ile C uzantıları yazmak.

## C-Level Optimizasyonlar ve Python İç Yapısı

### Python C Extension Nedir?

Python, yorumlamalı (interpreted) bir dil olduğu için C/C++ ile yazılmış kodlara göre daha yavaştır. Ancak Python'un altında **CPython** interpreter'ı C ile yazılmıştır ve C kütüphanelerini doğrudan çağırabilir.

**C Extension:** Python'un C API'si kullanılarak yazılmış modüllerdir. Performans kritik kodlar C'ye taşınarak büyük hız kazanımları sağlanır.

### CPython İç Yapısı

1. **Bytecode Compilation**
   - Python kodu önce **bytecode**'a derlenir (`.pyc` dosyaları).
   - Bytecode, CPython VM tarafından yorumlanır.

2. **GIL (Global Interpreter Lock)**
   - CPython'da bir seferde sadece bir thread Python bytecode çalıştırabilir.
   - I/O işlemlerinde GIL bırakılır, ama CPU-bound işlemlerde bottleneck olur.
   - Çözüm: `multiprocessing` (ayrı süreçler, GIL yok).

3. **Object Model**
   - Her Python objesi `PyObject` struct'ının bir uzantısıdır.
   - Referans sayma (`Py_INCREF`, `Py_DECREF`) ile bellek yönetimi.

### C-Level Optimizasyon Teknikleri

#### 1. **Built-in Functions (Yerleşik Fonksiyonlar)**

Python'un `sorted()`, `min()`, `max()` gibi fonksiyonları C ile yazılmıştır ve çok hızlıdır.

**Örnek:**
```python
# Yavaş (Python loop)
result = []
for x in data:
    result.append(x * 2)

# Hızlı (C-level list comprehension)
result = [x * 2 for x in data]

# En hızlı (C-level map)
result = list(map(lambda x: x * 2, data))
```

#### 2. **NumPy Kullanımı**

NumPy, C ve Fortran ile yazılmış, vektörel işlemler için optimize edilmiştir.

```python
import numpy as np

# Python loop (yavaş)
arr = [i for i in range(1000000)]
result = [x * 2 for x in arr]

# NumPy (100x hızlı)
arr = np.arange(1000000)
result = arr * 2
```

#### 3. **Cython ile C Extension Yazma**

Cython, Python benzeri syntax ile C kodu üretir.

**Örnek: `cython_sort.pyx`**

```cython
def quick_sort_cython(list arr):
    cdef int n = len(arr)
    cdef int i, j, pivot
    
    # C değişkenleri ile hızlı işlem
    for i in range(n):
        for j in range(i+1, n):
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
    return arr
```

**Derleme:**
```bash
cythonize -i cython_sort.pyx
```

#### 4. **PyPy Kullanımı**

PyPy, JIT (Just-In-Time) derleyici ile Python kodunu dinamik olarak makine koduna çevirir. Uzun çalışan scriptlerde 5-10x hız artışı sağlayabilir.

### Proje için C-Level İyileştirmeler

1. **NumPy Arrays Kullanımı**
   - `list` yerine `numpy.ndarray` kullanmak (C seviyesinde bitişik bellek).

2. **Cython ile Kritik Döngüleri Optimize Etmek**
   - `partition`, `heapify` gibi döngü yoğun fonksiyonları Cython ile yazmak.

3. **Multiprocessing ile Paralelleştirme**
   - Karşılaştırma ekranında farklı algoritmaları paralel çalıştırmak.

4. **C Extension Yazmak**
   - En performans kritik algoritmalar (örneğin, radix sort) için saf C extension.

### Örnek: C Extension ile Quick Sort

**`quick_sort_c.c`**

```c
#include <Python.h>

void quick_sort_internal(int *arr, int low, int high) {
    if (low < high) {
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        int pi = i + 1;
        
        quick_sort_internal(arr, low, pi - 1);
        quick_sort_internal(arr, pi + 1, high);
    }
}

static PyObject* quick_sort_c(PyObject* self, PyObject* args) {
    PyObject* py_list;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &py_list)) {
        return NULL;
    }
    
    Py_ssize_t n = PyList_Size(py_list);
    int *arr = malloc(n * sizeof(int));
    
    for (Py_ssize_t i = 0; i < n; i++) {
        arr[i] = PyLong_AsLong(PyList_GetItem(py_list, i));
    }
    
    quick_sort_internal(arr, 0, n - 1);
    
    for (Py_ssize_t i = 0; i < n; i++) {
        PyList_SetItem(py_list, i, PyLong_FromLong(arr[i]));
    }
    
    free(arr);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"quick_sort", quick_sort_c, METH_VARARGS, "Quick sort in C"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "quick_sort_c",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_quick_sort_c(void) {
    return PyModule_Create(&module);
}
```

**`setup.py`**

```python
from setuptools import setup, Extension

module = Extension('quick_sort_c', sources=['quick_sort_c.c'])

setup(name='QuickSortC',
      version='1.0',
      ext_modules=[module])
```

**Derleme:**

```bash
python setup.py build_ext --inplace
```

**Kullanım:**

```python
import quick_sort_c

data = [5, 2, 8, 1, 9]
quick_sort_c.quick_sort(data)
print(data)  # [1, 2, 5, 8, 9]
```

## Teknik Dokümantasyon (Chatbot Bilgi Tabanı)

Bu bölüm, Chatbot'un algoritmaları ve sonuçları yorumlarken kullanacağı teknik bilgi tabanıdır.

Proje tipi: Algorithm Analysis & Performance Benchmarking  
Stack: Python (Algorithms), GUI (PySide6), Matplotlib

### 1. Mimari ve Teknik Altyapı (Architecture & Technical Foundation)

#### 1.1 Projenin Amacı (Objective)

Bu yazılım, teorik bilgisayar bilimlerinde öğretilen Asymptotic Notation (Asimptotik Notasyon) kavramlarının gerçek donanım üzerindeki davranışlarını simüle eder. Amaç, Big-O ($O$) notasyonunun her zaman gerçek çalışma süresini (Running Time) tam olarak yansıtmadığını, donanım mimarisi (CPU Cache, Branch Prediction) ve dilin (Python) çalışma yapısının sonuçları nasıl etkilediğini göstermektir.

#### 1.2 Ölçüm Metodolojisi (Measurement Methodology)

- **Time Measurement (Zaman Ölçümü):** İşletim sistemi arka plan süreçlerini (OS jitter) minimize etmek için `time.perf_counter()` kullanılır. Bu fonksiyon, yüksek çözünürlüklü bir *monotonic clock* sağlar.
- **Memory Profiling (Bellek Profillemesi):** Bu projede `tracemalloc` ile Python ek bellek (peak delta) ve `psutil` ile süreç RSS *peak* bellek ölçülür.  
  - İleri seviye analiz için `tracemalloc` kullanılarak *current memory* ve *peak memory* değerleri de elde edilebilir.
  - **Current Memory:** Anlık kullanılan bellek.
  - **Peak Memory:** Algoritma çalışırken ulaşılan maksimum bellek tepe noktası.

#### 1.3 Thread Safety ve Concurrency (Eşzamanlılık)

- **QThread Kullanımı:** GUI'nin donmaması için uzun süren işlemler (karşılaştırma, chatbot API çağrısı) arka plan thread'lerinde çalışır.
- **Signal-Slot Mekanizması:** Thread'ler arası güvenli iletişim için Qt'nin signal-slot sistemi kullanılır.
- **GIL (Global Interpreter Lock):** Python'da bir seferde tek thread çalışabilir, ama I/O işlemlerinde (API çağrısı) GIL serbest bırakılır.

### 2. Algoritmaların Derinlemesine Analizi (Deep Dive)

Chatbot, algoritmaları anlatırken aşağıdaki *Internal Mechanics* (İç Mekanikler) bilgilerini kullanmalıdır.

#### A. Quick Sort (Hızlı Sıralama) - Recursive Divide & Conquer

- **Mekanizma:** Bir pivot seçilir. Dizi, pivottan küçükler (sol) ve büyükler (sağ) olarak *partitioning* işlemine tabi tutulur.
- **Pivot Stratejisi:**
  - **Naive:** İlk veya son eleman (sıralı dizilerde $O(n^2)$ felaketine yol açar).
  - **Optimized:** *Median-of-three* (baş, orta, son arasından ortanca).
  - **Randomized:** Rastgele pivot (worst case'i engeller, beklenen $O(n \log n)$).
- **Neden Hızlı?** 
  - **Cache Locality (Önbellek Yerelliği):** Bellek üzerinde bitişik alanlarda işlem yaptığı için CPU cache hit oranı yüksektir.
  - **In-Place:** Ek bellek gerektirmez ($O(\log n)$ stack hariç).
  - **Tail Recursion Optimization:** Modern derleyiciler tail call'ları optimize eder.
- **Python Sınırı:** Rekürsif implementasyonlarda Python'un *Recursion Limit* (varsayılan ~1000) sınırı vardır. Bu projede iteratif quick sort kullanıldığı için stack taşması riski azaltılmıştır.
- **Complexity:** Time: $O(n \log n)$ avg, $O(n^2)$ worst; Space: $O(\log n)$ (stack).

#### B. Merge Sort (Birleştirmeli Sıralama) - Stable Divide & Conquer

- **Mekanizma:** Dizi rekürsif olarak tek eleman kalana kadar parçalanır, sonra sıralı bir şekilde birleştirilir (*merging*).
- **Kritik Özellik - Stability (Kararlılık):** Değeri eşit olan elemanların sıralama sonrası birbirlerine göre konumlarını korumasını sağlar.
  - **Örnek:** `[(2, "a"), (2, "b"), (1, "c")]` sıralandığında `[(1, "c"), (2, "a"), (2, "b")]` olur (a ve b'nin sırası korunur).
- **Bellek Maliyeti:** Birleştirme işlemi için orijinal dizi boyutunda ($O(n)$) yardımcı dizi gerekir.
- **Parallelization Potansiyeli:** Alt diziler bağımsız olduğu için paralel çalıştırılabilir.
- **Complexity:** Time: $O(n \log n)$ (her durumda), Space: $O(n)$.

#### C. Heap Sort (Yığın Sıralaması) - Selection on Steroids

- **Mekanizma:** Dizi önce Max-Heap yapılır, kök (en büyük) en sona alınır ve *heapify* tekrar uygulanır.
- **Array Mapping:** i indexli elemanın çocukları `2i+1` ve `2i+2`'dedir. Bu, tree yapısını array'de saklamaya yarar.
- **Heap Özelliği:** Parent node, child node'lardan büyüktür (max-heap) veya küçüktür (min-heap).
- **Dezavantajı:** Teorik olarak Quick Sort ile aynı olsa da (O(n log n)), bellek erişimi dağınık olduğu için **cache miss** oranı yüksektir ve pratikte yavaştır.
- **Avantajı:** Worst case $O(n \log n)$ garanti eder (quick sort'tan farklı olarak).
- **Complexity:** Time: $O(n \log n)$, Space: $O(1)$ (in-place).

#### D. Shell Sort (Kabuk Sıralaması) - Generalized Insertion Sort

- **Mekanizma:** Insertion Sort'un geliştirilmiş halidir. Aralıklı (gap) elemanları karşılaştırır, gap'i kademeli olarak azaltır.
- **Gap Sequences (Aralık Dizileri):** Performans kullanılan gap dizisine bağlıdır.  
  - **Shell Sequence:** $N/2, N/4, ..., 1$ (bu projede kullanılan dizidir, basit ama optimal değil).
  - **Knuth Sequence:** $(3^k - 1) / 2$ → `1, 4, 13, 40, ...` (daha iyi performans sağlar).
  - **Hibbard Sequence:** $2^k - 1$ → `1, 3, 7, 15, ...`.
  - **Sedgewick Sequence:** Hybrid formül (en iyi bilinen performans).
- **Kullanım Alanı:** Recursion kullanmadığı için gömülü sistemlerde (embedded systems) avantajlıdır.
- **Neden Hızlı:** Uzak elemanları erken taşıdığı için insertion sort'tan çok daha az yer değiştirme yapar.
- **Complexity:** Gap dizisine göre değişir, genelde $O(n^{1.25})$ ile $O(n^{1.5})$ arası. Space: $O(1)$.

#### E. Radix Sort (Taban Sıralaması) - Non-Comparative

- **Mekanizma:** Sayıları karşılaştırmaz. Sayıları basamaklarına (digit) göre kutulara (buckets) dağıtır. **LSD (Least Significant Digit)** yöntemi kullanılır (en sağdaki basamaktan başlar).
- **Counting Sort Subroutine:** Her basamak için arka planda **Counting Sort** mantığı uygulanır (kararlı sıralama).
- **Kısıtlar:** 
  - Sadece tamsayılar veya sabit uzunluklu stringlerde çalışır.
  - Negatif sayılar için ek işlem gerekir (offset eklemek veya iki aşamalı sıralama).
- **Avantajı:** Karşılaştırma yapmadığı için teorik olarak $O(n)$'ye yaklaşabilir (d ve k sabit ise).
- **Dezavantajı:** Bellek kullanımı yüksektir ($O(n+k)$, k = digit aralığı).
- **Complexity:** Time: $O(d \cdot (n+k))$, Space: $O(n+k)$.

### 3. Veri Seti Senaryoları ve Beklenen Davranışlar (Test Scenarios)

Chatbot, "Neden bu sonuç çıktı?" sorusuna bu senaryolarla cevap vermelidir.

#### 3.1 Random Data (Rastgele Veri)

- **Beklenen:** Quick Sort genellikle en hızlıdır; Merge Sort ve Heap Sort onu takip eder.
- **Neden:** Quick Sort'un iç döngüsü basittir ve CPU optimizasyonlarına (branch prediction, cache locality) uygundur.
- **Teorik vs Pratik:** Merge Sort de $O(n \log n)$ olsa da, ek bellek tahsisi ve kopyalama overhead'i nedeniyle yavaştır.

#### 3.2 Sorted / Nearly Sorted Data (Sıralı / Neredeyse Sıralı)

- **Tehlike:** Pivot stratejisi kötüyse Quick Sort worst case ($O(n^2)$) gösterebilir.
  - **Örnek:** İlk eleman pivot seçilirse, sıralı dizide her partition tek eleman ayırır → $n$ seviye derinlik.
- **Kazanan:** 
  - **Shell Sort:** Insertion sort mantığıyla, az yer değiştirme yaptığı için avantajlıdır.
  - **Timsort** (Python'un `sorted()` fonksiyonu): Kısmen sıralı veride $O(n)$'ye yaklaşır.
- **Merge Sort:** Veri düzeninden etkilenmez, her zaman $O(n \log n)$.

#### 3.3 Reverse Sorted Data (Ters Sıralı)

- **Etki:** Kötü pivot seçimi Quick Sort için felaket olabilir (örneğin, son eleman pivot ve reverse sorted → worst case).
- **Kazanan:** 
  - **Merge Sort ve Heap Sort:** Veri düzeninden etkilenmez, istikrarlı süre verir ($O(n \log n)$).
  - **Radix Sort:** Karşılaştırma yapmadığı için veri düzeninden bağımsızdır.
- **Shell Sort:** Gap sequence'e bağlı olarak ortalama performans gösterir.

### 4. Donanım Mimarisi ve Performans (Hardware Architecture Impact)

#### 4.1 CPU Cache Hierarchy (Önbellek Hiyerarşisi)

Modern CPU'lar üç seviye cache kullanır:
- **L1 Cache:** 32-64 KB, 1-2 clock cycle latency (en hızlı).
- **L2 Cache:** 256-512 KB, 5-10 clock cycle latency.
- **L3 Cache:** 4-32 MB, 20-50 clock cycle latency (tüm core'lar paylaşır).
- **RAM:** GB seviyesinde, 100-200 clock cycle latency (en yavaş).

**Cache-Friendly Algoritmalar:**
- **Quick Sort:** Partition işlemi bitişik bellek alanlarında yapılır → yüksek cache hit.
- **Merge Sort:** Yardımcı dizi kullanır, ekstra bellek erişimi → düşük cache hit.
- **Heap Sort:** Parent-child ilişkisi rastgele bellek erişimi gerektirir → çok düşük cache hit.

#### 4.2 Branch Prediction (Dal Tahmini)

CPU, dallanma (if-else) yönünü tahmin eder. Yanlış tahmin pahalıdır (pipeline flush, 10-20 clock cycle kayıp).

**Branch-Friendly Kodlar:**
- Tahmin edilebilir dallanmalar (örneğin, döngü sonu).
- `if` yerine branchless arithmetic (`min = a < b ? a : b` → `min = a + (b - a) * (a > b)`).

**Quick Sort'ta Branch Prediction:**
- Pivot karşılaştırmaları genellikle 50/50 dağılır → branch predictor'ü zorlar.
- Randomized pivot ile dallanma daha tahmin edilemez hale gelir.

#### 4.3 SIMD (Single Instruction, Multiple Data)

Modern CPU'lar, tek bir instruction ile birden fazla veri işleyebilir (örneğin, AVX512 ile 16 float aynı anda).

**SIMD Kullanımı:**
- NumPy ve vektörel işlemler SIMD kullanır.
- Pure Python loops SIMD kullanamaz.

**Örnek:**
```python
# SIMD yok (Python loop)
result = [x * 2 for x in range(1000000)]

# SIMD var (NumPy)
import numpy as np
arr = np.arange(1000000)
result = arr * 2  # 8-16x hızlı
```

### 5. Örnek Diyalog Senaryoları (Chatbot Training Set)

#### Senaryo 1: Teori vs Pratik

**Kullanıcı:** "Merge Sort ile Quick Sort arasındaki fark ne? İkisi de $O(n \log n)$ değil mi?"

**Bot Cevabı:**  
"Harika bir soru! Teorik olarak ikisi de $O(n \log n)$ karmaşıklığına sahiptir ancak pratikte işler değişir:

1. **Bellek Yönetimi:** Merge Sort, birleştirme için ekstra $O(n)$ bellek ister. Quick Sort ise in-place çalışır (sadece $O(\log n)$ stack).

2. **Donanım Uyumu:** Quick Sort, ardışık bellek erişimi sayesinde **cache hit** oranını artırır. Merge Sort, yardımcı dizi kullandığı için cache miss oranı daha yüksektir.

3. **Stability:** Merge Sort **stable** olduğu için eşit elemanların sırası korunur; Quick Sort bunu garanti etmez.

4. **Worst Case:** Quick Sort, kötü pivot seçiminde $O(n^2)$'ye düşebilir. Merge Sort her zaman $O(n \log n)$ garanti eder.

5. **Pratik Performans:** 10,000 elemanlık rastgele verinde, Quick Sort genellikle Merge Sort'tan 1.5-2x daha hızlıdır (CPU cache sayesinde)."

#### Senaryo 2: Hata Analizi

**Kullanıcı:** "100.000 elemanlık ters sıralı veride Quick Sort hata verdi, neden?"

**Bot Cevabı:**  
"Bu, klasik bir **pivot seçimi + recursion limit** problemidir. İşte detaylar:

1. **Pivot Seçimi:** Eğer pivot her zaman uçtan (ilk veya son eleman) seçilirse, ters sıralı dizide her partition sadece bir eleman ayırır. Bu durumda:
   - Derinlik: $n$ seviye (100,000 seviye)
   - Karmaşıklık: $O(n^2)$ (her seviyede $O(n)$ iş)

2. **Python Recursion Limit:** Python varsayılan olarak yaklaşık 1000 recursive çağrıya izin verir (`sys.getrecursionlimit()`). 100,000 seviye derinlik, bu limiti aşar ve `RecursionError` oluşur.

3. **Çözüm:**
   - **Median-of-three pivot:** Baş, orta, son arasından ortanca seçilir → worst case'i engeller.
   - **Randomized pivot:** Rastgele pivot seçimi → beklenen $O(n \log n)$.
   - **Iterative Quick Sort:** Bu projede kullanılan yöntem, stack taşması riskini azaltır.

4. **Sonuç:** Ters sıralı veride Merge Sort veya Heap Sort kullanmak daha güvenlidir, çünkü veri düzeninden etkilenmezler."

#### Senaryo 3: Bellek Optimizasyonu

**Kullanıcı:** "Radix Sort neden Merge Sort'tan daha fazla bellek kullanıyor?"

**Bot Cevabı:**  
"İki algoritmanın bellek kullanımı farklı nedenlerden kaynaklanır:

**Merge Sort:**
- $O(n)$ ek bellek: Birleştirme sırasında yardımcı dizi (geçici kopyalar).
- Python list'leri referans tuttuğu için, toplam bellek $n \times \text{pointer\_size}$ kadardır.

**Radix Sort:**
- $O(n + k)$ ek bellek:
  - $n$: Bucket'lara dağıtılan elemanlar için.
  - $k$: Her basamak için bucket sayısı (0-9 arası 10 bucket).
- Her basamak işlenirken, elemanlar bucket'lara kopyalanır ve geri birleştirilir.
- Örneğin, 5 basamaklı sayılar için 5 kez $O(n + 10)$ bellek tahsisi yapılır.

**Neden Radix Sort daha fazla kullanır:**
- Radix Sort, her basamak için ayrı bucket array'leri oluşturur.
- Merge Sort, sadece bir kez yardımcı dizi tahsis eder.

**Sonuç:** Büyük sayı aralıklarında (örneğin, 1 milyon elemanlı dizi, her eleman 10 basamaklı), Radix Sort'un bellek kullanımı Merge Sort'tan 2-3x daha fazla olabilir."

#### Senaryo 4: Veri Seti Etkisi

**Kullanıcı:** "Kısmen sıralı veride Shell Sort neden Quick Sort'tan hızlı çıktı?"

**Bot Cevabı:**  
"Harika bir gözlem! Bu, Shell Sort'un tasarım felsefesinden kaynaklanır:

**Shell Sort'un Avantajı:**
- Kısmen sıralı veride, elemanlar zaten birbirlerine yakındır.
- Shell Sort, büyük gap'lerle başladığı için, uzak elemanları erken taşır ve dizi hızla "neredeyse sıralı" hale gelir.
- Son adımda (gap=1, yani Insertion Sort), çok az yer değiştirme yapılır.

**Quick Sort'un Dezavantajı:**
- Kısmen sıralı veri, Quick Sort için best case değildir (rastgele veri daha iyidir).
- Eğer pivot stratejisi median-of-three ise, kısmen sıralı veride pivot her zaman orta değerde olabilir, bu da dengesiz partition'lara yol açar.

**Sonuç:** Kısmen sıralı veride Shell Sort ve Insertion Sort, Quick Sort'tan daha performanslı olabilir. Python'un `sorted()` fonksiyonu da bu nedenle **Timsort** kullanır (Merge Sort + Insertion Sort hybrid'i, kısmen sıralı veride $O(n)$ bile olabilir)."

### 6. Grafik Yorumlama Rehberi (Visualization Guide)

#### 6.1 Zaman Grafiği (Time Chart)

- **Eğri eğimleri:** 
  - $O(n^2)$ eğrisi parabolik olarak dikleşir (Shell Sort kötü durum, Quick Sort worst case).
  - $O(n \log n)$ eğrisi neredeyse doğrusal ama hafif kıvrımlıdır.
  - $O(n)$ eğrisi tamamen doğrusaldır (Radix Sort best case).

- **Örnek Yorumlama:**
  - 1000 eleman → Quick Sort: 0.01s, Merge Sort: 0.015s
  - 10,000 eleman → Quick Sort: 0.12s, Merge Sort: 0.18s
  - 100,000 eleman → Quick Sort: 1.5s, Merge Sort: 2.3s
  - **Sonuç:** Quick Sort, Merge Sort'tan ~1.5x hızlıdır (cache locality avantajı).

#### 6.2 Bellek Grafiği (Memory Chart)

- **Ek Bellek (tracemalloc):**
  - Heap Sort ve Shell Sort: Neredeyse sıfır (in-place).
  - Quick Sort: $O(\log n)$ (stack, çok düşük).
  - Merge Sort: $O(n)$ (yardımcı dizi).
  - Radix Sort: $O(n + k)$ (en yüksek, bucket array'leri).

- **Toplam Peak Bellek (psutil RSS):**
  - Veri boyutuna bağlı olarak artış gösterir.
  - Python interpreter overhead'i (10-20 MB) her algoritma için sabittir.
  - Radix Sort ve Merge Sort, daha yüksek peak RSS gösterir.

#### 6.3 Standart Sapma (Std Dev)

- **Düşük Std Dev:** Algoritma tutarlıdır (örneğin, Merge Sort).
- **Yüksek Std Dev:** Algoritma veri düzenine veya sistem yüküne duyarlıdır (örneğin, Quick Sort).

**Örnek:**
- Quick Sort: avg=0.5s, std=0.05s → %10 varyasyon.
- Merge Sort: avg=0.7s, std=0.01s → %1.4 varyasyon.

**Sonuç:** Merge Sort daha **predictable** (öngörülebilir), Quick Sort daha **performant** ama dalgalı.

### 7. İleri Seviye Konular (Advanced Topics)

#### 7.1 Hybrid Sorting (Hibrit Sıralama)

Birden fazla algoritmayı birleştirmek:
- **Timsort:** Merge Sort + Insertion Sort (Python'un `sorted()` fonksiyonu).
- **Introsort:** Quick Sort + Heap Sort (C++ `std::sort`).
  - Quick Sort ile başlar, recursion derinliği çok artarsa Heap Sort'a geçer.

#### 7.2 External Sorting (Dışsal Sıralama)

RAM'e sığmayan büyük veri setleri için:
- Veriyi parçalara böl, her parçayı bellekte sırala, disk'e yaz.
- Parçaları **k-way merge** ile birleştir.

#### 7.3 Parallel Sorting (Paralel Sıralama)

- **Merge Sort:** Her alt dizi bağımsız thread'de sıralanabilir.
- **Quick Sort:** Partition sonrası sol ve sağ bağımsızdır.
- **Sample Sort:** Parallel quick sort'un genelleştirilmiş hali.

#### 7.4 GPU Sorting (GPU Tabanlı Sıralama)

- **Thrust (CUDA):** GPU'da parallel sorting.
- **Bitonic Sort:** GPU-friendly, $O(n \log^2 n)$ ama çok paralel.

## Chatbot Entegrasyonu

Chatbot, README içeriğini sistem prompt olarak OpenAI API'ye gönderir ve kullanıcı sorularını bu içerik üzerinden yanıtlar.

### API Key Ayarı

Seçenek 1: `.env` dosyası (önerilir)
```bash
cp .env.example .env
# .env içine OPENAI_API_KEY değerini yapıştırın
```

Mac/Linux:
```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Windows (PowerShell):
```powershell
setx OPENAI_API_KEY "YOUR_KEY_HERE"
```

Opsiyonel model seçimi:
```bash
export OPENAI_MODEL="gpt-4o-mini"
```

### Kullanım

1) GUI'yi çalıştır: `python -m sorting_lab.gui.app`
2) **Chatbot** sekmesine git.
3) Sorunu yaz ve **Gönder**'e bas.
4) README güncellendiğinde **README Yenile** butonunu kullan.

Gizlilik notu: API key'i asla git'e eklemeyin. `.env` veya terminal ortam değişkeni olarak kullanın.

## Testler

```bash
pytest
```

Test kapsamı:
- `tests/test_algorithms.py`: Her algoritmanın doğruluğunu test eder.
- `tests/test_data_gen.py`: Veri üretim fonksiyonlarını test eder.
- `tests/test_metrics.py`: Metrik ölçümlerinin doğruluğunu test eder.

## Troubleshooting

### Genel Sorunlar

- **ModuleNotFoundError**: `pip install -e .` çalıştırın.
- **Grafikler görünmüyor**: Matplotlib backend/PySide6 uyumunu kontrol edin (`matplotlib.use('QtAgg')`).
- **Chatbot hata veriyor**: `OPENAI_API_KEY` set edildi mi kontrol edin (`echo $OPENAI_API_KEY`).

### Performans Sorunları

- **GUI donuyor**: Uzun süren işlemler QThread'de mi çalışıyor kontrol edin.
- **Bellek taşması**: Çok büyük veri setlerinde (>10M eleman) sistem belleği yetersiz kalabilir.
- **Yavaş animasyon**: FPS değerini azaltın (örneğin, 30 FPS → 10 FPS).

### Platform-Specific Sorunlar

- **macOS**: Qt framework yüklü değilse `brew install qt` çalıştırın.
- **Windows**: Visual C++ Redistributable gerekebilir.
- **Linux**: `libGL.so.1` hatası için `sudo apt-get install libgl1-mesa-glx`.

---

Sorting Lab, algoritmaların teorik ve pratik performansını karşılaştırmak isteyen öğrenciler için tam kapsamlı bir laboratuvar ortamı sunar. Bu README, projenin her yönünü detaylı şekilde açıklar ve chatbot'un kullanıcılara en iyi şekilde yardımcı olmasını sağlar.
