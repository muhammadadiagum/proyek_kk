# 02_code — Kode Eksperimen

Folder ini berisi seluruh kode Python untuk membangun instance, menjalankan eksperimen, menganalisis hasil, dan menghasilkan naskah.

## Struktur

| Berkas | Fungsi |
|---|---|
| `model.py` | Model data internal, fungsi penilaian objektif, dan validator independen. |
| `ctt_parser.py` | Parser instance ITC2007 CB-CTT (`.ctt`) ke model internal. |
| `generate_instances.py` | Generator instance sintetis dari jadwal basis yang dijamin layak. |
| `methods.py` | Tiga metode: greedy konstruktif, GA standar, dan GA + repair. |
| `make_jobs.py` | Membuat spesifikasi job untuk pilot, main, dan ablation. |
| `run_experiment.py` | Runner paralel; menulis satu baris JSON per run ke `03_experiments/raw/*.jsonl`. |
| `pilot_select.py` | Memilih konfigurasi dari hasil pilot sesuai aturan design lock. |
| `analyze.py` | Menghitung tabel statistik, tabel per keluarga, biaya, dan gambar. |
| `ablation_compare.py` | Membandingkan varian ablation dengan konfigurasi terkunci. |
| `report_numbers.py` | Membuat lembar angka Markdown dari tabel hasil. |
| `build_manuscript.py` | Membangun naskah final dari sumber Markdown + tabel + referensi. |
| `md2docx.py` | Konversi Markdown ke DOCX; ekspor PDF memakai Word di Windows. |
| `make_slides.py` | Membuat slide presentasi dari tabel dan gambar. |
| `export_raw.py` | Mengekspor JSONL mentah ke CSV/XLSX untuk paket submit. |
| `requirements.txt` | Dependensi Python. |

## Urutan alur kerja

1. `ctt_parser.py` — membaca instance benchmark.
2. `generate_instances.py` — membuat instance sintetis.
3. `make_jobs.py` — membuat daftar job.
4. `run_experiment.py` — menjalankan pilot/main/ablation.
5. `pilot_select.py` — mengunci konfigurasi dari pilot.
6. `analyze.py` — menghasilkan tabel dan gambar.
7. `ablation_compare.py` — analisis ablation.
8. `report_numbers.py` — lembar angka naskah.
9. `build_manuscript.py` — membangun naskah.
10. `md2docx.py` — DOCX/PDF.
11. `make_slides.py` dan `export_raw.py` — paket presentasi/submit.

## Catatan

- Jalankan dari root proyek dengan virtual environment proyek, misalnya `./.venv/bin/python 02_code/analyze.py ...`.
- Skrip analisis tidak menulis angka manual; angka berasal dari `03_experiments/raw/*.jsonl` dan tabel di `04_results/tables/`.
- Naskah Indonesia dibangun dengan `build_manuscript.py --lang id`; sumbernya ada di `05_manuscript/idn/`.
