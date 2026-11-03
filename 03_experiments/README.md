# 03_experiments — Rekaman Eksperimen

Folder ini menyimpan rekaman mentah setiap run dan log eksekusinya. Ini adalah sumber utama angka yang dilaporkan di naskah.

## `raw/`

Satu baris JSON = satu run. Setiap baris memuat konfigurasi, hasil, jejak evaluasi, versi kode, dan identitas host.

| Berkas | Run | Status | Keterangan |
|---|---:|---|---|
| `pilot.jsonl` | 472 | `ok` | Pilot untuk pemilihan konfigurasi. |
| `main.jsonl` | 861 | `ok` | Hasil utama: 21 instance uji. |
| `ablation.jsonl` | 2.100 | `ok` | Ablation: 21 instance × 5 varian × 20 seed. |
| `pilot_aborted_keyerror.jsonl` | 457 | gagal awal | Artefak run pilot yang gagal karena `KeyError`; tidak dipakai. |
| `pilot_smoke.jsonl` | 12 | uji coba | Smoke test awal; tidak dipakai di hasil. |

Total run final yang diolah: **3.433** (472 + 861 + 2.100).

## `logs/`

Log stdout/stderr dari setiap eksekusi, diberi nama menurut suite dan timestamp.

- `run_pilot_20261029_051153.log`
- `run_pilot_20261029_051245.log`
- `run_pilot_20261029_052251.log`
- `run_main_20261029_053222.log`
- `run_ablation_20261029_054939.log`

## Catatan

- Jangan mengedit `*.jsonl` secara manual; file ini adalah bukti eksekusi.
- Angka di `04_results/` dan `05_manuscript/` harus dapat ditelusuri kembali ke file di `raw/`.
- `pilot_aborted_keyerror.jsonl` dan `pilot_smoke.jsonl` sengaja dipertahankan sebagai jejak, tetapi tidak termasuk analisis final.
