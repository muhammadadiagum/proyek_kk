# 07_literature — Literatur dan Referensi

Folder ini berisi matriks literatur, metadata referensi terverifikasi, dan daftar referensi yang dipakai naskah.

| Berkas | Isi |
|---|---|
| `matrix.md` | Matriks literatur: paper, fokus, metode, relevansi, dan posisi terhadap studi ini. |
| `refs_verified.json` | Metadata referensi terverifikasi (DOI, judul, penulis, tahun, venue, volume, halaman). |
| `references.md` | Daftar referensi format APA yang dihasilkan dari metadata terverifikasi. |
| `references.bib` | Daftar referensi format BibTeX. |
| `build_references.py` | Skrip pembangun `references.md` dan `references.bib` dari `refs_verified.json`. |

## Alur

1. Metadata diverifikasi dan disimpan di `refs_verified.json`.
2. `build_references.py` membaca file itu.
3. Skrip menghasilkan `references.md` dan `references.bib`.
4. `02_code/build_manuscript.py` menyisipkan daftar referensi ke naskah.

## Catatan

- Jangan mengedit `references.md`/`references.bib` secara manual; edit `refs_verified.json` lalu jalankan ulang `build_references.py`.
- `matrix.md` adalah catatan naratif untuk penentuan posisi penelitian, bukan daftar referensi final.
