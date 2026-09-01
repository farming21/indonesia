# farming21/indonesia

Website publik untuk koleksi video kategori Indonesia dan Papua.

## Cara Kerja
1. Data video disimpan di `videos.json`.
2. GitHub Actions menjalankan `generate.py` secara otomatis.
3. Website di-generate dan di-deploy ke GitHub Pages.

## Struktur
- `videos.json`: Data utama (Source of Truth).
- `generate.py`: Script generator Python.
- `templates/`: Template HTML dasar.
- `covers/`: Gambar thumbnail video.
