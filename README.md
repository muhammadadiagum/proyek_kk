# Repair-Based, Budget-Aware Genetic Algorithm for Curriculum-Based Course Timetabling

Proyek Tugas Besar Kecerdasan Komputasional (S2 Teknologi Informasi) — Kelompok 1
(F5522630001 Slamet Riyadi, F5522630002 Muhammad Adi Agum, F5522630003 Akbar Tri
Wicaksono, F5522630004 I Ketut Divta Suryawan).

Pertanyaan riset: *pada anggaran evaluasi yang sama, apakah GA dengan repair
kendala-hard menemukan jadwal feasible lebih sering / dengan pelanggaran hard
lebih rendah daripada GA standar, dan berapa biaya anggaran dari repair?*

Domain: Curriculum-Based Course Timetabling (CB-CTT, ITC2007 Track 2).

## Struktur

```
00_config/       design_lock.md, jobs_*.json, config_final.json, pilot_selection.csv
01_data/         benchmark/ (ITC2007 .ctt + .json), synthetic/ (9), pilot/ (2)
02_code/         ctt_parser.py, model.py, generate_instances.py, methods.py,
                 make_jobs.py, run_experiment.py, pilot_select.py, analyze.py,
                 report_numbers.py, ablation_compare.py, build_manuscript.py,
                 md2docx.py, make_slides.py, requirements.txt
03_experiments/  raw/ (*.jsonl mentah per run), logs/ (stdout tiap eksekusi)
04_results/      tables/ (CSV + XLSX), figures/ (PNG 300 dpi)
05_manuscript/   manuscript.md / .docx / .pdf, numbers_main.md
06_package/      slide, cover letter, calon jurnal, kontribusi anggota,
                 tabel klaim → bukti
07_literature/   matriks literatur, references.md/.bib, refs_verified.json
```

## Hasil ringkas (semua dari `03_experiments/raw/`)

| Suite | Run | Isi |
|---|---|---|
| pilot | 472 | 36 konfigurasi repair × 4 instance dev × 3 seed + baseline GA + greedy |
| main | 861 | 21 instance × 3 metode × 20 seed (+ baseline greedy) |
| ablation | 2100 | 5 varian × 21 instance × 20 seed |

| Metode | Instance layak (mayoritas seed) | Median H | Median P | Generasi | Runtime (s) | Porsi repair |
|---|---|---|---|---|---|---|
| Greedy | 9/21 | 11 | 38 | 0 | 0.05 | 0.00 |
| GA | 10/21 | 1 | 95 | 208 | 4.35 | 0.00 |
| GA-R | 19/21 | 0 | 63 | 68 | 8.60 | 0.67 |

Wilcoxon berpasangan per instance: H *p* = 0.0033, P *p* = 0.0003, Cliff's δ =
−1.00. McNemar kelayakan: *p* = 0.0039. Pada 12 instance benchmark: GA layak
17/240 run, GA-R 173/240 run. Pada 9 instance sintetis semua metode layak;
keunggulan repair di sana hanya pada penalti preferensi. Semua angka dapat
diregenerasi dan dipetakan per klaim di `06_package/claims_evidence.md`.

## Lingkungan

- WSL2 (Linux 6.18, x86_64), Intel i7-13650HX (14 vCPU), RAM 8 GB, tanpa GPU.
- Python 3.14.4; numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2,
  openpyxl 3.1.5, python-docx, python-pptx (`02_code/requirements.txt`, `.venv`).
- Eksekusi paralel: `run_experiment.py --jobs 12` (multiprocessing, satu proses
  per run; tiap proses single-thread untuk numpy).
- Ekspor PDF memakai Microsoft Word di host Windows (COM otomatis lewat
  `md2docx.py --pdf`); tidak ada LibreOffice/pandoc di mesin ini.

## Reproduksi

```bash
uv venv .venv --python /usr/bin/python3 && . .venv/bin/activate
uv pip install -r 02_code/requirements.txt

python 02_code/ctt_parser.py 01_data/benchmark/raw   # .ctt → .json
python 02_code/generate_instances.py                 # 9 sintetis + 3 pilot
python 02_code/make_jobs.py pilot
python 02_code/run_experiment.py --spec 00_config/jobs_pilot.json --jobs 12
python 02_code/pilot_select.py                       # → 00_config/config_final.json
python 02_code/make_jobs.py main
python 02_code/run_experiment.py --spec 00_config/jobs_main.json --jobs 12 \
       --out 03_experiments/raw/main.jsonl
python 02_code/make_jobs.py ablation
python 02_code/run_experiment.py --spec 00_config/jobs_ablation.json --jobs 12 \
       --out 03_experiments/raw/ablation.jsonl

python 02_code/analyze.py --raw 03_experiments/raw/main.jsonl --label main
python 02_code/analyze.py --raw 03_experiments/raw/ablation.jsonl --label ablation
python 02_code/ablation_compare.py                   # varian vs konfigurasi terkunci
python 02_code/report_numbers.py --label main         # lembar angka naskah
python 02_code/build_manuscript.py --label main       # → 05_manuscript/manuscript.md
python 02_code/md2docx.py 05_manuscript/manuscript.md \
       05_manuscript/manuscript.docx --pdf            # → DOCX + PDF
python 02_code/make_slides.py                         # → 06_package/slides_kelompok1.pptx
```

Waktu eksekusi terukur pada mesin ini: pilot 472 run ≈ 8 menit, main 861 run ≈
14 menit, ablation 2100 run ≈ 33 menit (`--jobs 12`).

## Data

- **Sintetis** (`01_data/synthetic/`): dibangun *feasible by construction* — sebuah
  jadwal basis dibuat lebih dulu, lalu ketersediaan dosen dipersempit dengan
  syarat jadwal basis tetap valid. Parameter `share` generator = proporsi slot
  *tambahan* di luar slot yang dipakai jadwal basis: A 0.6, B 0.3, C 0.1, sehingga
  rata-rata ketersediaan per sesi menjadi 0.667 (A), 0.433 (B), 0.233 (C). Jadwal
  basis disimpan (`base_solution`) sehingga kelayakan dapat diverifikasi ulang;
  seed generator tercatat di dalam berkas.
- **Benchmark** (`01_data/benchmark/raw/*.ctt`): ITC2007 Track 2 (CB-CTT),
  instance `comp01`–`comp21`, format asli tanpa modifikasi. Sumber: mirror
  repositori GitHub `Docheinstein/itc2007-cct` (situs asli QUB tidak lagi
  menyediakan unduhan langsung). Atribusi: ITC2007 *International Timetabling
  Competition*, Track 2, digunakan untuk penelitian.
- Pembagian: **dev/pilot** = `pilot45B`, `pilot45C`, `comp13`, `comp14`;
  **test** = 9 sintetis + `comp01`–`comp12`.

## Akuntansi evaluasi

Satu evaluasi = satu penilaian objektif atas satu kandidat: (a) penilaian
lengkap satu jadwal, atau (b) satu kandidat perpindahan/tukar-sesi yang
diperiksa repair. Inisialisasi dan repair dibebankan; pembangunan indeks
okupansi tidak (pembukuan, terlihat pada runtime). Batas: 10.000 evaluasi per
run. Rincian: `00_config/design_lock.md` §5.

## Format catatan per run

Satu baris JSON di `03_experiments/raw/<suite>.jsonl`:

`instance`, `instance_name`, `family`, `n`, `n_slots`, `n_rooms`, `fill`,
`method`, `seed`, `tag`, `cfg` (konfigurasi penuh), `status` (`ok`),
`best_H`, `best_P`, `feasible`, `evals`, `evals_to_first_feasible`,
`generations`, `repair_probes`, `repair_sessions`, `repair_swaps`,
`repair_failures`, `budget_limited`, `repair_share`, `runtime_s`,
`validated_H`, `validated_P` (validator independen), `trace` (jejak
(evaluasi, best_H, best_P)), `wall_clock`, `pid`.

Log stdout tiap eksekusi: `03_experiments/logs/run_<suite>_<timestamp>.log`
(memuat identitas host, CPU, RAM, versi Python/numpy, jumlah run, waktu).

## Naskah & paket submit

- Naskah: `05_manuscript/manuscript.docx` (utama), `manuscript.pdf`, sumber
  `manuscript_source.md` (teks, satu baris per paragraf) → `build_manuscript.py`
  mengisi tabel, daftar referensi, dan placeholder angka → `manuscript.md`
  (berkas jadi, tidak diedit tangan) → `md2docx.py` (Word + PDF).
- Versi bahasa Indonesia (pendamping, bukan naskah submit): `05_manuscript/idn/`
  berisi `manuscript_source_id.md` (terjemahan sumber), `manuscript_id.docx`,
  `manuscript_id.pdf`, dan gambar berlabel Indonesia di `04_results/figures/idn/`.
  Dibangun dengan `build_manuscript.py --lang id` (angka tetap dari CSV yang sama)
  dan `analyze.py --lang id --figdir 04_results/figures/idn`.
- Slide 15 halaman: `06_package/slides_kelompok1.pptx`.
- Cover letter: `06_package/cover_letter.md`.
- Dua calon jurnal terverifikasi: `06_package/journal_candidates.md`.
- Kontribusi anggota: `06_package/member_contributions.md`.
- Pemetaan klaim → bukti: `06_package/claims_evidence.md`.
- Kunci desain (sebelum test dievaluasi) + amendment log: `00_config/design_lock.md`.
