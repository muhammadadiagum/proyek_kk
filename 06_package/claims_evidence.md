# Tabel pemetaan klaim → bukti eksekusi

Setiap klaim di naskah harus punya baris di sini. Kolom "Cara memeriksa" adalah
perintah yang dijalankan dari akar proyek, dan hasilnya harus sama dengan angka
pada naskah. Semua angka berasal dari `03_experiments/raw/*.jsonl`, tidak ada
yang diketik dari ingatan.

Perintah dasar (sekali jalan, menghasilkan semua tabel & gambar):

```bash
.venv/bin/python 02_code/analyze.py --raw 03_experiments/raw/main.jsonl --label main
.venv/bin/python 02_code/report_numbers.py --label main
```

| # | Klaim pada naskah | Lokasi | Bukti | Cara memeriksa |
|---|---|---|---|---|
| C1 | GA-R layak pada mayoritas seed di 19/21 instance; GA 10/21; Greedy 9/21 | Abstract, §5.1, Tabel 2 | `04_results/tables/main_descriptive.csv` kolom `feasible_rate` | `report_numbers.py` §2 (kolom "Feasible instances") |
| C2 | Median H = 0 (GA-R), 1 (GA), 11 (Greedy); mean H 0.42 / 4.42 / 13.62 | §5.1, Tabel 2 | `main_descriptive.csv` (`median_H`, `mean_H`) | `report_numbers.py` §2 |
| C3 | Median P = 63 (GA-R) vs 95 (GA) vs 38 (Greedy) | Abstract, §5.1 | `main_descriptive.csv` (`median_P`) | `report_numbers.py` §2 |
| C4 | Wilcoxon H: W = 0, p = 0.0033, Cliff's δ = −1.00; P: p = 0.0003 | Abstract, §5.1, Tabel 3 | `04_results/tables/main_stats.csv` | `report_numbers.py` §5 |
| C5 | Friedman H χ² = 23.53 (p < 0.001); P χ² = 10.47 (p = 0.0053); post-hoc Holm semua p ≤ 0.0066 | §5.1 | `main_stats.csv` baris `friedman` & `posthoc_wilcoxon_holm` | `report_numbers.py` §5 |
| C6 | McNemar: 9 instance diskordan, semua berpihak GA-R, p = 0.0039 | §5.1 | `main_stats.csv` baris `mcnemar_exact` | `report_numbers.py` §5 |
| C7 | Pada 9 instance sintetis semua metode layak di semua seed (feasible share 1.00) | §5.2, §5.5 | `main_by_family.csv` baris pattern A/B/C | `cat 04_results/tables/main_by_family.csv` |
| C8 | Median P sintetis per pola: GA-R 0.00/0.00/0.00; GA 0.00/2.00/4.50; Greedy 23.0/24.0/17.0 | §5.2 | `main_descriptive.csv` (`pattern`, `median_P`) | `report_numbers.py` §4 |
| C9 | Benchmark: greedy tidak pernah layak (median H = 24); GA 17/240 run layak; GA-R 173/240 | §5.2 | `main_descriptive.csv` + hitung dari JSONL (`feasible`) | lihat skrip pemeriksa di bawah |
| C10 | Benchmark median H 0 vs 7; median P 106.5 vs 171.0 | §5.2 | `main_by_family.csv` baris `benchmark` | `report_numbers.py` §3–§4 |
| C11 | comp01 (H median 4 vs 9) dan comp05 (3 vs 10) gagal dicapai semua metode | §5.2 | `main_descriptive.csv` baris comp01/comp05 | `report_numbers.py` §6 |
| C12 | Porsi anggaran repair 66.9%; 2.84 juta probe; 36% probe gagal | Abstract, §5.3, §6 | `main_cost.csv`, jumlah `repair_probes`/`repair_failures` di JSONL | skrip pemeriksa di bawah |
| C13 | Generasi 68 vs 208 (3.1×); runtime 8.60 s vs 4.35 s (benchmark 21.9 vs 16.6) | Abstract, §5.3 | `main_cost.csv`, `main_descriptive.csv` (`median_generations`, `median_runtime_s`) | `report_numbers.py` §2 |
| C14 | Evaluasi ke layak pertama di benchmark: GA median 20 (17 run), GA-R median 3.002 (173 run) | §5.3 | `main_descriptive.csv` (`median_evals_to_first`) + hitung per run dari JSONL | skrip pemeriksa di bawah |
| C15 | comp01 okupansi ruang 0.889 dengan 6 ruang; comp05 139 kurikulum untuk 54 mata kuliah | §5.2 | `01_data/benchmark/raw/comp01.ctt`, `comp05.ctt`, `main_descriptive.csv` (`fill`) | `head -20 01_data/benchmark/raw/comp05.ctt` |
| C16 | 861 run utama, semua lolos validator independen (`validated_H == best_H`) | §5 | `main.jsonl` kolom `status`, `validated_H` | skrip pemeriksa di bawah |
| C17 | Hasil ablation (5 varian × 21 instance × 20 seed = 2.100 run) | §5.4, Tabel 6 | `03_experiments/raw/ablation.jsonl`, `04_results/tables/ablation_descriptive.csv` | `analyze.py --raw .../ablation.jsonl --label ablation` |
| C18 | Konfigurasi dipilih dari pilot dengan aturan terkunci (k=5, 1 kandidat, tanpa swap, pm=1/n) | §4.4 | `00_config/pilot_selection.csv`, `00_config/config_final.json` | `cat 00_config/config_final.json` |
| C19 | Pilot 472 run; GA-R pada grid pilot layak X/…; GA standar layak Y/… (angka persis dari JSONL) | §4.4 | `03_experiments/raw/pilot.jsonl` | `build_manuscript.py` mengisi dari JSONL |
| C20 | 20 seed per metode per instance; unit analisis = instance (median 20 seed) | §3.3, §4.4 | `00_config/jobs_main.json`, `main_descriptive.csv` kolom `runs` | `python -c` hitung `runs` per (instance, method) |

## Skrip pemeriksa (klaim yang dihitung dari JSONL mentah)

```bash
cd /home/aec/_AO/PATHs/S2/AO_PAPERs/COURSE_EXAM/KK
.venv/bin/python - <<'PY'
import json, statistics as st, collections
rows = [json.loads(l) for l in open('03_experiments/raw/main.jsonl')]
bm = [r for r in rows if r['family'] != 'synthetic']
for m in ('greedy', 'ga_std', 'ga_repair'):
    sub = [r for r in bm if r['method'] == m]
    e2f = [r['evals_to_first_feasible'] for r in sub if r.get('evals_to_first_feasible') is not None]
    print(m, 'benchmark runs', len(sub), 'feasible', len(e2f),
          'median e2f', st.median(e2f) if e2f else None)
print('repair probes', sum(r.get('repair_probes', 0) for r in rows if r['method'] == 'ga_repair'))
print('repair failures', sum(r.get('repair_failures', 0) for r in rows if r['method'] == 'ga_repair'))
bad = [r for r in rows if r['validated_H'] != r['best_H'] or r['validated_P'] != r['best_P']]
print('validated mismatch:', len(bad), 'of', len(rows))
per = collections.Counter((r['instance_name'], r['method']) for r in rows)
print('runs per (instance, method):', sorted(set(per.values())))
PY
```

Keluaran yang diharapkan (dari run 2026-10-29): `ga_std` 240 run, 17 layak,
median e2f 20; `ga_repair` 240 run, 173 layak, median e2f 3002; `greedy` 0 layak;
probe 2.838.573; kegagalan probe 1.013.220; mismatch 0 dari 861; GA dan GA-R
masing-masing 20 run per instance, sedangkan greedy 1 run per instance karena
deterministik (nilai `runs` yang muncul: 1 dan 20).

## Hal yang **tidak** diklaim

- Tidak ada klaim kebaruan metode repair; naskah menyebut repair sebagai teknik
  yang sudah dikenal (Coello Coello, 2002) dan memposisikan kontribusi pada
  pengukuran yang dinormalisasi anggaran.
- Tidak ada klaim bahwa tangga ketersediaan sintetis membuktikan H1; §5.2 dan §7
  menyatakan sebaliknya.
- Tidak ada nomor APC, kuartil, atau faktor dampak jurnal yang diklaim; lihat
  catatan di `06_package/journal_candidates.md`.
