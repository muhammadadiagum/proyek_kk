# 00_config — Konfigurasi dan Design Lock

Folder ini berisi aturan eksperimen yang dikunci sebelum pengujian, konfigurasi final hasil pilot, dan spesifikasi job untuk setiap suite.

## Struktur

| Berkas | Isi |
|---|---|
| `design_lock.md` | Protokol eksperimen yang dikunci sebelum melihat hasil test: pertanyaan riset, hipotesis, domain/instance, metode, akuntansi anggaran, metrik, desain statistik, aturan berhenti, konfigurasi final, dan amendment log. |
| `config_final.json` | Konfigurasi yang dipilih dari pilot dan dipakai untuk run utama. |
| `jobs_pilot.json` | Spesifikasi 472 run pilot. |
| `jobs_main.json` | Spesifikasi 861 run utama. |
| `jobs_ablation.json` | Spesifikasi 2.100 run ablation. |

## `config_final.json`

Konfigurasi terkunci yang dipakai di suite utama:

| Parameter | Nilai |
|---|---|
| `pm` | `1/n` |
| `repair_max_sessions` | 5 |
| `repair_attempts` | 1 |
| `swap_attempts` | 0 |
| `pm_std` | `1/n` |
| `budget` | 10.000 evaluasi |
| `pop_size` | 50 |
| `pc` | 0.8 |
| `elitism` | 2 |
| `seed_mode` | `greedy` |

Konfigurasi ini dipilih dari `03_experiments/raw/pilot.jsonl` dengan aturan: proporsi run layak tertinggi, median `H` terendah, median `P` terendah, lalu porsi anggaran repair terendah.

## `design_lock.md`

Dokumen ini adalah protokol yang dikunci sebelum instance uji dievaluasi. Bagian utamanya:

1. Pertanyaan riset
2. Hipotesis
3. Domain dan instance
4. Metode
5. Akuntansi anggaran evaluasi
6. Metrik
7. Desain statistik
8. Aturan berhenti dan pengecualian
9. Konfigurasi final
10. Reproduksibilitas
11. Amendment log

## `jobs_*.json`

Setiap file berisi `suite`, `budget`, dan daftar `runs`. Satu entri run memuat `instance`, `method`, `seed`, `cfg`, dan `tag`.

| Suite | Jumlah run |
|---|---:|
| Pilot | 472 |
| Main | 861 |
| Ablation | 2.100 |

## Catatan

- `design_lock.md` dan `config_final.json` tidak boleh diubah setelah run test dimulai; perubahan harus dicatat di amendment log.
- Job dibuat oleh `02_code/make_jobs.py` dan dieksekusi oleh `02_code/run_experiment.py`.
- Konfigurasi final berasal dari pilot, bukan dari hasil test.
