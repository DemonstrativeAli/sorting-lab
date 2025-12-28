Sorting Lab – Comparative Sorting Analysis
=========================================

Quick, Heap, Shell, Merge ve Radix sort algoritmalarını GUI üzerinden deneyip, farklı veri setlerinde süre/bellek performanslarını ölçmek ve görselleştirmek için hazırlanmış proje.

Kurulum
-------
1) Sanal ortam (opsiyonel): `python -m venv venv && source venv/bin/activate`
2) Bağımlılıklar: `pip install -r requirements.txt`
3) Paket editable kurulum (önerilir): `pip install -e .`

Çalıştırma
----------
- CLI toplu deney: `python -m sorting_lab.cli --algos quick,heap,merge --sizes 1000,10000 --dataset random --runs 3`
- GUI: `python -m sorting_lab.gui.app`
  - **Tek Deneme**: tek algoritma için süre/bellek ölçümü, giriş/çıktı önizleme
  - **Karşılaştırma**: birden fazla algoritma için tablo + bar grafik
  - **Adım Adım**: algoritma ilerleyişini bar grafik animasyonu ile izleme (hız ayarlı)

Dizin Yapısı
------------
- `data/inputs` örnek giriş setleri; `generated` deney sırasında üretilecekler; `results` metrik çıktı; `figures` grafikler
- `src/sorting_lab/algorithms` algoritma implementasyonları
- `src/sorting_lab/utils` veri üretimi, metrik ve profil araçları
- `src/sorting_lab/gui` PySide6 GUI; `screens` alt ekranlar (tek koşu, karşılaştırma, adım adım)
- `src/sorting_lab/analysis` toplu deney koşuları ve rapor üretimi
- `tests/` birim testler
- `docs/` rapor şablonları ve deney notları

Notlar
------
- Adım adım görselleştirme için 800 adım limiti vardır (büyük n için performans). Hız kaydırıcısı kare gecikmesini ms cinsinden ayarlar.
- Radix sort negatif sayıları desteklemez.
