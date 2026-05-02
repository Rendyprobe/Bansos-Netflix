## Requirements

Gunakan virtualenv project:

```bash
myenv/bin/python -m pip install playwright
```

Browser Chromium akan diunduh otomatis ke folder `.ms-playwright/` saat pertama kali mode copy dipakai. Kalau ingin install manual:

```bash
myenv/bin/python -m playwright install chromium
```

## Usage

Jalankan:

```bash
./run.sh
```

Alternatif langsung:

```bash
myenv/bin/python nf-token-generator.py
```

Contoh alur `Dapatkan Bahan`:

```text
Selectable items:
1. Indonesia
2. Malaysia
3. Singapore
Choose country/item: Singapore
Saved copied text to input.txt.
```

Kamu bisa memilih dengan nomor dari daftar.


## Notes

Mode `Dapatkan Bahan` menimpa `input.txt` setiap kali copy berhasil.

Setelah opsi 1 atau 2 selesai, program kembali ke menu utama. Pilih `0` untuk keluar.
