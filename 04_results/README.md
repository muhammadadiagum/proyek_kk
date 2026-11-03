# 04_results — Tabel dan Gambar Hasil

Folder ini berisi hasil olahan dari `03_experiments/raw/*.jsonl`. Semua angka di sini dihitung oleh skrip di `02_code/`, bukan ditulis manual.

## `tables/`

| Berkas | Isi |
|---|---|
| `main_descriptive.csv` | Ringkasan per instance dan metode untuk suite utama. |
| `main_stats.csv` | Uji statistik berpasangan (Wilcoxon, Friedman, McNemar, Cliff's delta, koreksi Holm). |
| `main_cost.csv` | Biaya komputasi: waktu, generasi, porsi repair, evaluasi sampai layak. |
| `main_by_family.csv` | Kinerja menurut keluarga instance dan pola ketersediaan. |
| `main_tables.xlsx` | Gabungan tabel utama dalam Excel. |
| `ablation_descriptive.csv` | Ringkasan per instance/varian ablation. |
| `ablation_compare.csv` | Perbandingan setiap varian ablation dengan konfigurasi terkunci. |
| `ablation_stats.csv` | Statistik ablation. |
| `ablation_cost.csv` | Biaya komputasi ablation. |
| `ablation_by_family.csv` | Kinerja ablation menurut keluarga/pola. |
| `ablation_tables.xlsx` | Gabungan tabel ablation dalam Excel. |
| `pilot_selection.csv` | Ringkasan konfigurasi pilot dan aturan pemilihannya. |

## `figures/`

- `main_fig1_convergence.png` — kurva konvergensi.
- `main_fig2_quality_box.png` — sebaran kualitas solusi.
- `main_fig3_feasible_rate.png` — proporsi run layak.
- `main_fig4_cost.png` — biaya evaluasi/repair.
- `main_fig5_scaling.png` — pengaruh ukuran instance.

- `ablation_fig1_convergence.png` sampai `ablation_fig5_scaling.png` — padanan untuk ablation.

- `idn/` — versi gambar utama dengan label Bahasa Indonesia (5 gambar).

## Catatan

- Gambar dihasilkan pada 300 dpi oleh `02_code/analyze.py`.
- Jika data mentah berubah, jalankan ulang `analyze.py` dan `ablation_compare.py`; jangan mengedit CSV/gambar secara manual.
