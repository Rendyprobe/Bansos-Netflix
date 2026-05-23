## Bansos Netflix

Tool terminal untuk mengambil bahan cookie Netflix, menyimpannya ke `input.txt`,
lalu menjalankan generator URL lewat `eksekusi.py`.

## Struktur Folder

```text
Bansos-Netflix/
├── run.sh
├── nf-token-generator.py
├── eksekusi.py
├── input.txt
├── Bahan/
└── myenv/
```

Keterangan:

- `run.sh`: launcher utama.
- `nf-token-generator.py`: menu utama program.
- `eksekusi.py`: script generate URL dari isi `input.txt`.
- `input.txt`: file bahan aktif yang akan dibaca saat generate URL.
- `Bahan/`: folder untuk menyimpan banyak file bahan `.txt`.
- `myenv/`: virtualenv Python project.

## Persiapan Awal

Masuk ke folder project:

```bash
cd /home/rendy/Downloads/Bansos-Netflix
```

Install dependency Playwright di virtualenv project:

```bash
myenv/bin/python -m pip install playwright
```

Browser Chromium akan diunduh otomatis ke folder `.ms-playwright/` saat mode
ambil dari web pertama kali dipakai. Kalau ingin install manual:

```bash
myenv/bin/python -m playwright install chromium
```

Pastikan `run.sh` bisa dieksekusi:

```bash
chmod +x run.sh
```

## Cara Menjalankan

Jalankan program utama:

```bash
./run.sh
```

Alternatif langsung:

```bash
myenv/bin/python nf-token-generator.py
```

Menu utama:

```text
Test Cookie Parser

1. Generate URL
2. Dapatkan Bahan
0. Keluar

Pilih menu:
```

## Menu 1: Generate URL

Pilih `1` untuk menjalankan `eksekusi.py`.

Alur:

1. Program membaca isi `input.txt`.
2. Program menjalankan `eksekusi.py`.
3. Hasil generate URL ditampilkan oleh script tersebut.

Pastikan `input.txt` sudah berisi bahan yang benar sebelum memilih menu ini.

## Menu 2: Dapatkan Bahan

Pilih `2` untuk mengisi ulang `input.txt`.

Submenu:

```text
Dapatkan Bahan

1. Ambil dari web
2. Ambil dari file tersimpan
0. Kembali

Pilih sumber bahan:
```

## Ambil Dari Web

Pilih `1` di submenu `Dapatkan Bahan`.

Alur:

1. Program membuka website target lewat Playwright.
2. Program menampilkan daftar negara atau item yang bisa dipilih.
3. Pilih item dengan nomor atau nama persis.
4. Program klik tombol copy dari website.
5. Hasil copy ditulis ke `input.txt`.

Contoh:

```text
Selectable items:
1. Indonesia
2. Malaysia
3. Singapore
Choose country/item: Singapore
Saved copied text to input.txt.
```

## Ambil Dari File Tersimpan

Pilih `2` di submenu `Dapatkan Bahan`.

Program akan mencari file `.txt` secara random dari folder `Bahan/`, lalu
menyalin isi file yang lolos ke `input.txt`.

Syarat file yang bisa dipilih:

1. File harus berada langsung di folder `Bahan/`.
2. File harus berekstensi `.txt`.
3. Isi file harus mengandung tulisan `Premium`.
4. Isi file harus punya baris tanggal relevan, misalnya `Next billing:`.
5. Tanggal tersebut harus lebih baru dari tanggal program dijalankan.

Contoh aturan tanggal:

- Jika program dijalankan tanggal 24, tanggal 24 tidak valid.
- Jika program dijalankan tanggal 24, tanggal 25, 26, 27, dan seterusnya valid.
- Jika program dijalankan tanggal 24 Mei, tanggal 1 Juni juga valid.

Contoh isi file yang valid:

```text
– Plan: Premium
– Next billing: June 6, 2026
```

Contoh output sukses:

```text
Saved Bahan/[Premium] [1 payments] [extra false] [MA] [email@example.com] [Configure by Hydra_x001].txt to input.txt (tanggal terbaca: June 6, 2026).
```

Catatan penting:

- Pemilihan file dilakukan random dari semua kandidat yang lolos.
- File dengan `Plan: Standard`, `Basic`, `Mobile`, atau tanpa tulisan `Premium`
  tidak dipakai.
- Tanggal teknis di cookie seperti `datestamp=...` tidak dipakai sebagai acuan.
- Mode ini akan menimpa isi `input.txt`.

## Format Tanggal Yang Didukung

Program membaca tanggal dari baris berlabel seperti:

```text
Next billing: 25 May 2026
Next billing: May 25, 2026
Tanggal: 25 Mei 2026
Expiry: 25/05/2026
```

Nama bulan yang umum dipakai dalam beberapa bahasa sudah didukung, termasuk
Indonesia dan English.

## Alur Kerja Yang Disarankan

1. Masukkan banyak file bahan `.txt` ke folder `Bahan/`.
2. Jalankan `./run.sh`.
3. Pilih `2. Dapatkan Bahan`.
4. Pilih `2. Ambil dari file tersimpan`.
5. Pastikan program menampilkan pesan `Saved ... to input.txt`.
6. Kembali ke menu utama.
7. Pilih `1. Generate URL`.

## Troubleshooting

### `Tidak ada file .txt di folder Bahan`

Pastikan folder `Bahan/` ada dan berisi file `.txt`.

### `Tidak ada file .txt ... yang berisi Premium dan tanggalnya setelah hari ini`

Artinya tidak ada kandidat yang memenuhi semua syarat. Cek lagi:

- Isi file punya tulisan `Premium`.
- Ada baris tanggal seperti `Next billing:`.
- Tanggalnya lebih baru dari tanggal hari ini.
- File berada langsung di folder `Bahan/`, bukan di subfolder.

### Playwright belum terinstall

Jalankan:

```bash
myenv/bin/python -m pip install playwright
```

Jika Chromium belum tersedia:

```bash
myenv/bin/python -m playwright install chromium
```

### `input.txt` tidak berubah

Pastikan menjalankan script dari folder yang benar:

```bash
cd /home/rendy/Downloads/Bansos-Netflix
./run.sh
```

Setelah mode ambil bahan sukses, terminal harus menampilkan:

```text
Saved ... to input.txt
```

## Catatan

- Setelah menu `1` atau `2` selesai, program kembali ke menu utama.
- Pilih `0` untuk keluar.
- `input.txt` adalah bahan aktif terakhir yang berhasil disimpan.
