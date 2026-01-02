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
- [Fonksiyon Referansı](#fonksiyon-referansı)
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

### 3) Adım Adım Görselleştirme (Live View)

- **Adım kaydı:** Algoritma, her adımda dizi durumunu kaydeder.
- **Canlı animasyon:** Sıralama süreci bar grafik olarak canlı izlenir.
- **FPS kontrolü:** Animasyon hızı FPS ile ayarlanır.
- **Adım limiti:** Büyük veri setlerinde performans için adım sayısı sınırlandırılır.

### 4) Chatbot

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
| Shell Sort | Gap’e bağlı | Gap’e bağlı | ~O(n²) | O(1) |
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

## Fonksiyon Referansı

Aşağıdaki liste, proje içindeki fonksiyonların rolünü özetler. GUI tarafında birçok yardımcı metot bulunur; burada ana akış ve kritik metotlar listelenmiştir.

### `src/sorting_lab/algorithms`

- `quick_sort._record_state`: Adım kaydı için dizi kopyasını kaydeder.
- `quick_sort.sort`: Median-of-three pivot + iteratif quicksort. (steps opsiyonel)
- `quick_sort.median_of_three`: Pivot seçimi için 3 eleman kıyaslar.
- `quick_sort.partition`: Pivot etrafında parçalama.

- `heap_sort._record_state`: Adım kaydı.
- `heap_sort.sort`: Heap tabanlı sıralama.
- `heap_sort.heapify`: Heap düzeni oluşturur.

- `merge_sort._record_state`: Adım kaydı.
- `merge_sort.sort`: Merge sort ana fonksiyonu.
- `merge_sort.merge_sort`: Recursive bölme.
- `merge_sort.merge`: İki alt diziyi birleştirir.

- `shell_sort._record_state`: Adım kaydı.
- `shell_sort.sort`: Gap tabanlı insertion sort.

- `radix_sort.sort`: LSD radix sort ana fonksiyonu.
- `radix_sort.record`: Yerel adım kaydı fonksiyonu.

- `algorithms.run_algorithm`: Algoritmayı key ile çalıştırır.
- `algorithms.available_algorithms`: Kullanılabilir algoritmalar listesi.
- `algorithms.keys`: Algoritma anahtarlarını döndürür.

### `src/sorting_lab/utils`

- `data_gen.random_array`: Rastgele veri seti.
- `data_gen.partially_sorted_array`: Kısmi sıralı veri seti.
- `data_gen.reverse_sorted_array`: Ters sıralı veri seti.
- `data_gen.generate`: Dataset adına göre uygun veri üretir.

- `metrics.measure`: Çalışma süresini, Python ek bellek (tracemalloc peak) ve toplam RSS peak değerlerini ölçer.
- `metrics.run_trials`: Birden fazla deneme yapar, avg/std çıkarır.
- `metrics.MeasureResult`: Tek ölçüm sonucu modeli.
- `metrics.TrialStats`: Çoklu deneme istatistiği modeli.

- `profiling.profile_func`: cProfile ile profiling yapar.
- `visualizer.plot_runtime`: Matplotlib ile basit runtime grafiği.

### `src/sorting_lab/analysis`

- `runner.run_experiments`: Toplu deney çalıştırır, CSV çıktısı üretir.
- `report.generate_report`: CSV’den basit HTML rapor üretir.

### `src/sorting_lab/cli.py`

- `parse_args`: CLI argümanlarını okur.
- `main`: CLI akışı, run_experiments çağırır.

### `src/sorting_lab/gui/app.py`

- `MainWindow`: Ana pencere + tab yönetimi.
- `run`: PySide6 uygulamasını başlatır.

### `src/sorting_lab/gui/screens/single_run.py`

- `SingleRunView`: Tek algoritma çalıştırma ekranı.
- `_on_run`: Veriyi üretir, algoritmayı çalıştırır, sonucu UI’a yazar.
- `_render_preview`: Giriş/çıkış önizleme tablosu üretir.
- `_update_algo_info`: Algoritma açıklamalarını günceller.
- `_set_status`, `_pulse_status`: Durum etiketi animasyon ve güncelleme.
- `_sync_card_heights`: Kart yüksekliklerini eşitler.

### `src/sorting_lab/gui/screens/compare.py`

- `CompareWorker`: Arka planda karşılaştırma çalıştırır.
  - `run`: Algoritmaları sırayla ölçer, sonuçları DataFrame olarak döndürür.
  - `stop`: Çalışmayı durdurur.
- `CompareView`: Karşılaştırma UI ekranı.
  - `_on_compare`: Karşılaştırma sürecini başlatır.
  - `_render_table`: Sonuç tablosunu doldurur.
  - `_render_chart`: Metrik grafiğini hazırlar.
  - `_start_animation`: Grafik animasyonunu başlatır.
  - `_toggle_detail_chart`: Detaylı grafiği göster/gizle.
  - `_reset_chart`: Grafiği sıfırlar.

### `src/sorting_lab/gui/screens/live_view.py`

- `ArrayCanvas`: Bar grafik çizimi; `paintEvent` ile canlı render.
- `LiveView._on_run`: Veriyi üretir ve adımları kaydeder.
- `LiveView._advance`: Her frame’de bir adımı gösterir.
- `LiveView._on_stop`: Animasyonu durdurur.

### `src/sorting_lab/gui/screens/chatbot.py`

- `ChatWorker`: OpenAI API çağrısını arka planda yapar.
- `ChatbotView`: Chatbot UI.
  - `_load_readme`: README dosyasını okur.
  - `_build_system_message`: README’yi system prompt’a ekler.
  - `_on_send`: Kullanıcı mesajını işler ve API çağrısını başlatır.
  - `_on_response`: Yanıtı sohbet ekranına yazar.
  - `_reload_readme`: README’yi yeniden yükler.

## Teknik Dokümantasyon (Chatbot Bilgi Tabanı)

Bu bölüm, Chatbot’un algoritmaları ve sonuçları yorumlarken kullanacağı teknik bilgi tabanıdır.

Proje tipi: Algorithm Analysis & Performance Benchmarking  
Stack: Python (Algorithms), GUI (PySide6), Matplotlib

### 1. Mimari ve Teknik Altyapı (Architecture & Technical Foundation)

#### 1.1 Projenin Amacı (Objective)

Bu yazılım, teorik bilgisayar bilimlerinde öğretilen Asymptotic Notation (Asimptotik Notasyon) kavramlarının gerçek donanım üzerindeki davranışlarını simüle eder. Amaç, Big-O ($O$) notasyonunun her zaman gerçek çalışma süresini (Running Time) tam olarak yansıtmadığını, donanım mimarisi (CPU Cache, Branch Prediction) ve dilin (Python) çalışma yapısının sonuçları nasıl etkilediğini göstermektir.

#### 1.2 Ölçüm Metodolojisi (Measurement Methodology)

- Time Measurement (Zaman Ölçümü): İşletim sistemi arka plan süreçlerini (OS jitter) minimize etmek için `time.perf_counter()` kullanılır. Bu fonksiyon, yüksek çözünürlüklü bir *monotonic clock* sağlar.
- Memory Profiling (Bellek Profillemesi): Bu projede `tracemalloc` ile Python ek bellek (peak delta) ve `psutil` ile süreç RSS *peak* bellek ölçülür.  
  - İleri seviye analiz için `tracemalloc` kullanılarak *current memory* ve *peak memory* değerleri de elde edilebilir.
  - Current Memory: Anlık kullanılan bellek.
  - Peak Memory: Algoritma çalışırken ulaşılan maksimum bellek tepe noktası.

### 2. Algoritmaların Derinlemesine Analizi (Deep Dive)

Chatbot, algoritmaları anlatırken aşağıdaki *Internal Mechanics* (İç Mekanikler) bilgilerini kullanmalıdır.

#### A. Quick Sort (Hızlı Sıralama) - Recursive Divide & Conquer

- Mekanizma: Bir pivot seçilir. Dizi, pivottan küçükler (sol) ve büyükler (sağ) olarak *partitioning* işlemine tabi tutulur.
- Pivot Stratejisi:
  - Naive: İlk veya son eleman (sıralı dizilerde $O(n^2)$ felaketine yol açar).
  - Optimized: *Median-of-three* (baş, orta, son arasından ortanca).
- Neden Hızlı? Cache Locality (Önbellek Yerelliği) prensibine çok uygundur. Bellek üzerinde bitişik alanlarda işlem yaptığı için CPU cache hit oranı yüksektir.
- Python Sınırı: Rekürsif implementasyonlarda Python’un *Recursion Limit* sınırı vardır. Bu projede iteratif quick sort kullanıldığı için stack taşması riski azaltılmıştır.
- Complexity: Time: $O(n \log n)$ avg, Space: $O(\log n)$ (stack).

#### B. Merge Sort (Birleştirmeli Sıralama) - Stable Divide & Conquer

- Mekanizma: Dizi rekürsif olarak tek eleman kalana kadar parçalanır, sonra sıralı bir şekilde birleştirilir (*merging*).
- Kritik Özellik - Stability (Kararlılık): Değeri eşit olan elemanların sıralama sonrası birbirlerine göre konumlarını korumasını sağlar.
- Bellek Maliyeti: Birleştirme işlemi için orijinal dizi boyutunda ($O(n)$) yardımcı dizi gerekir.
- Complexity: Time: $O(n \log n)$ (her durumda), Space: $O(n)$.

#### C. Heap Sort (Yığın Sıralaması) - Selection on Steroids

- Mekanizma: Dizi önce Max-Heap yapılır, kök (en büyük) en sona alınır ve *heapify* tekrar uygulanır.
- Array Mapping: i indexli elemanın çocukları `2i+1` ve `2i+2`’dedir.
- Dezavantajı: Teorik olarak Quick Sort ile aynı olsa da (O(n log n)), bellek erişimi dağınık olduğu için pratikte yavaştır.
- Complexity: Time: $O(n \log n)$, Space: $O(1)$ (in-place).

#### D. Shell Sort (Kabuk Sıralaması) - Generalized Insertion Sort

- Mekanizma: Insertion Sort’un geliştirilmiş halidir. Aralıklı (gap) elemanları karşılaştırır.
- Gap Sequences: Performans kullanılan gap dizisine bağlıdır.  
  - Shell Sequence: $N/2, N/4, ...$ (bu projede kullanılan dizidir).
  - Knuth Sequence: $(3^k - 1) / 2$ (daha iyi performans sağlayabilir).
- Kullanım Alanı: Recursion kullanmadığı için gömülü sistemlerde (embedded systems) avantajlıdır.
- Complexity: Gap dizisine göre değişir, genelde $O(n^{1.25})$ ile $O(n^{1.5})$ arası. Space: $O(1)$.

#### E. Radix Sort (Taban Sıralaması) - Non-Comparative

- Mekanizma: Sayıları karşılaştırmaz. Sayıları basamaklarına (digit) göre kutulara (buckets) dağıtır. LSD (Least Significant Digit) yöntemi kullanılır.
- Counting Sort Subroutine: Her basamak için arka planda Counting Sort mantığı uygulanır.
- Kısıtlar: Sadece tamsayılar veya sabit uzunluklu stringlerde çalışır. Negatif sayılar için ek işlem gerekir.
- Complexity: Time: $O(d \cdot (n+k))$, Space: $O(n+k)$.

### 3. Veri Seti Senaryoları ve Beklenen Davranışlar (Test Scenarios)

Chatbot, “Neden bu sonuç çıktı?” sorusuna bu senaryolarla cevap vermelidir.

#### 3.1 Random Data (Rastgele Veri)

- Beklenen: Quick Sort genellikle en hızlıdır; Merge Sort ve Heap Sort onu takip eder.
- Neden: Quick Sort’un iç döngüsü basittir ve CPU optimizasyonlarına uygundur.

#### 3.2 Sorted / Nearly Sorted Data (Sıralı / Neredeyse Sıralı)

- Tehlike: Pivot stratejisi kötüyse Quick Sort worst case ($O(n^2)$) gösterebilir.
- Kazanan: Shell Sort (Insertion Sort mantığıyla) daha az yer değiştirdiği için avantajlı olabilir.

#### 3.3 Reverse Sorted Data (Ters Sıralı)

- Etki: Kötü pivot seçimi Quick Sort için felaket olabilir.
- Etki: Merge Sort ve Heap Sort veri düzeninden etkilenmez, istikrarlı süre verir ($O(n \log n)$).

### 4. Örnek Diyalog Senaryoları (Chatbot Training Set)

Kullanıcı: “Merge Sort ile Quick Sort arasındaki fark ne? İkisi de $O(n \log n)$ değil mi?”  
Bot Cevabı:  
“Harika bir soru! Teorik olarak ikisi de $O(n \log n)$ karmaşıklığına sahiptir ancak pratikte işler değişir:  
- Bellek Yönetimi: Merge Sort, birleştirme için ekstra $O(n)$ bellek ister. Quick Sort ise in-place çalışır.  
- Donanım Uyumu: Quick Sort, ardışık bellek erişimi sayesinde cache hit oranını artırır.  
- Stability: Merge Sort *stable* olduğu için eşit elemanların sırası korunur; Quick Sort bunu garanti etmez.”  

Kullanıcı: “100.000 elemanlık ters sıralı veride Quick Sort hata verdi, neden?”  
Bot Cevabı:  
“Bu, klasik bir *pivot seçimi + recursion limit* problemidir. Eğer pivot her zaman uçtan seçilirse, dizi tek taraflı bölünür ve $O(n^2)$ derinlik oluşur. Python varsayılan olarak yaklaşık 1000 recursive çağrıya izin verir. Bu projede iteratif quick sort kullanıldığı için bu problem azaltılmıştır; ama teorik olarak yanlış pivot seçimi yine performansı düşürür.”  

### 5. Grafik Yorumlama Rehberi (Visualization Guide)

- Eğri eğimleri: $O(n^2)$ eğrisi parabolik olarak dikleşir (Shell Sort kötü durum, Quick Sort kötü durum).  
  $O(n \log n)$ eğrisi ise neredeyse doğrusal ama hafif kıvrımlıdır.
- Bellek barları: Ek bellek grafiğinde Merge Sort ve Radix Sort daha yüksek görünür; Heap/Shell/Quick daha düşüktür. Toplam peak grafiği ise veri boyutuna bağlı olarak artış gösterir.

## Chatbot Entegrasyonu

Chatbot, README içeriğini sistem prompt olarak OpenAI API’ye gönderir ve kullanıcı sorularını bu içerik üzerinden yanıtlar.

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

1) GUI’yi çalıştır: `python -m sorting_lab.gui.app`
2) **Chatbot** sekmesine git.
3) Sorunu yaz ve **Gönder**’e bas.
4) README güncellendiğinde **README Yenile** butonunu kullan.

Gizlilik notu: API key’i asla git’e eklemeyin. `.env` veya terminal ortam değişkeni olarak kullanın.

## Testler

```bash
pytest
```

## Troubleshooting

- **ModuleNotFoundError**: `pip install -e .` çalıştırın.
- **Grafikler görünmüyor**: Matplotlib backend/PySide6 uyumunu kontrol edin.
- **Chatbot hata veriyor**: `OPENAI_API_KEY` set edildi mi kontrol edin.

---

Sorting Lab, algoritmaların teorik ve pratik performansını karşılaştırmak isteyen öğrenciler için tam kapsamlı bir laboratuvar ortamı sunar.
