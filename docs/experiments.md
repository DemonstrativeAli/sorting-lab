# Deney Planı

## Veri Setleri
- random: `data_gen.random_array(n)`
- partial: sıralı dizi + belirli oranda karıştırma (varsayılan %50)
- reverse: tamamen ters sıralı

## Boyutlar
- küçük: 1_000
- orta: 10_000
- büyük: 100_000 (GUI'de parametre olarak değiştirilebilir)

## Tekrarlar
- Her senaryo için en az 5 tekrar; ortalama ve std raporlanacak.

## Ölçüm
- Zaman: `time.perf_counter` ortalaması
- Bellek: `tracemalloc` peak delta + `psutil` RSS peak

## Komut (örn.)
```bash
python -m sorting_lab.cli --algos quick,heap,merge --sizes 1000,10000 --dataset random
```
