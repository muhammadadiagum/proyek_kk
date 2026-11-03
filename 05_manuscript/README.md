# 05_manuscript — Naskah

Folder ini berisi sumber naskah, hasil build, dan lembar angka. Ada dua versi bahasa: Inggris (root folder) dan Indonesia (`idn/`).

## Versi Inggris

| Berkas | Peran |
|---|---|
| `manuscript_source.md` | **Sumber teks** naskah Inggris; edit file ini, bukan hasil build. |
| `manuscript.md` | Hasil build dari source + tabel + referensi. |
| `manuscript.docx` | Versi Word. |
| `manuscript.pdf` | Versi PDF. |

## Versi Indonesia (`idn/`)

| Berkas | Peran |
|---|---|
| `manuscript_source_id.md` | **Sumber teks** naskah Indonesia; edit file ini. |
| `manuscript_id.md` | Hasil build naskah Indonesia. |
| `manuscript_id.docx` | Versi Word Indonesia. |
| `manuscript_id.pdf` | Versi PDF Indonesia. |

## Lembar angka

- `numbers_main.md` — ringkasan angka utama yang dipakai untuk pengecekan naskah.

## Cara build

Dari root proyek:

```bash
# Naskah Inggris
./.venv/bin/python 02_code/build_manuscript.py
./.venv/bin/python 02_code/md2docx.py 05_manuscript/manuscript.md 05_manuscript/manuscript.docx --pdf

# Naskah Indonesia
./.venv/bin/python 02_code/build_manuscript.py --lang id
./.venv/bin/python 02_code/md2docx.py 05_manuscript/idn/manuscript_id.md 05_manuscript/idn/manuscript_id.docx --pdf
```

## Catatan

- Jangan mengedit `manuscript.md`, `manuscript_id.md`, `.docx`, atau `.pdf` secara langsung; perubahan akan hilang saat build ulang.
- Semua placeholder `{{...}}` harus terisi; build gagal jika masih ada placeholder.
- PDF dibuat melalui Microsoft Word di Windows (`powershell.exe`) dari WSL. Jika interop Windows tidak aktif, DOCX tetap bisa dibuat tetapi PDF tidak.
