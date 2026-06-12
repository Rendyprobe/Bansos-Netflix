# Bansos Netflix 🎬

Tool otomatis untuk mengambil dan mengelola bahan Netflix, menyimpannya ke file, dan generate URL/token secara cepat dan mudah.

## 📋 Daftar Isi

- [Fitur](#-fitur)
- [Prasyarat](#-prasyarat)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [Struktur Folder](#-struktur-folder)
- [Troubleshooting](#-troubleshooting)
- [Lisensi](#-lisensi)

## ✨ Fitur

- ✅ Ambil bahan Netflix dari web secara otomatis (Desktop)
- ✅ Ambil bahan Netflix dari file tersimpan (Desktop & Termux)
- ✅ Generate URL dan token Netflix dengan cepat
- ✅ Kelola multiple file bahan di folder `Bahan/`
- ✅ Otomatis setup virtualenv dan dependencies
- ✅ Support untuk Desktop (Linux/Mac/Windows) dan Mobile (Termux/Android)

## 📦 Prasyarat

- **Python 3.7+**
- **pip** (Python package manager)
- **Git** (untuk clone repo)
- Browser Chromium (akan otomatis diunduh di desktop)

### Optional
- **Termux** (untuk penggunaan di Android)

## 🚀 Instalasi

### Untuk Desktop (Linux/Mac/Windows)

1. Clone repository:
```bash
git clone https://github.com/Rendyprobe/Bansos-Netflix.git
cd Bansos-Netflix
```

2. Buat virtualenv (jika belum ada):
```bash
python3 -m venv myenv
```

3. Aktifkan virtualenv:
   - **Linux/Mac:**
   ```bash
   source myenv/bin/activate
   ```
   - **Windows (CMD):**
   ```bash
   myenv\Scripts\activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Berikan permission ke `run.sh` (Linux/Mac):
```bash
chmod +x run.sh
```

### Untuk Mobile (Termux/Android)

1. Buka Termux dan install dependencies dasar:
```bash
pkg update && pkg upgrade
pkg install git python3 pip curl
```

2. Clone repository:
```bash
cd /sdcard/Download/
git clone https://github.com/Rendyprobe/Bansos-Netflix.git
cd Bansos-Netflix
```

3. Install Python dependencies:
```bash
pip install requests urllib3
```

## 📖 Penggunaan

### Cara Cepat (Desktop)

```bash
cd /home/rendy/Downloads/Bansos-Netflix
./run.sh
```

Script akan otomatis:
1. Membuat virtualenv jika belum ada
2. Install dependencies yang diperlukan
3. Download Chromium browser (jika belum ada)
4. Menampilkan menu utama

### Mode: Ambil dari Web (Desktop Only)

```bash
./run.sh --get-bahan-web
```

Atau pilih dari menu:
```
1. Dapatkan Bahan
1. Ambil dari web
```

### Mode: Ambil dari File Tersimpan

```bash
./run.sh --get-bahan-file
```

Atau pilih dari menu:
```
1. Dapatkan Bahan
2. Ambil dari file tersimpan
```

### Mode: Generate URL/Token

```bash
./run.sh --generate
```

Atau pilih dari menu:
```
2. Generate URL
```

### Termux (Android)

```bash
sh run.sh
```

Pilih menu:
```
2. Dapatkan Bahan
2. Ambil dari file tersimpan
1. Generate URL
```

## 📁 Struktur Folder

```text
Bansos-Netflix/
├── run.sh                      # Script launcher utama
├── run.bat                     # Script launcher untuk Windows
├── nf-token-generator.py       # Menu utama program
├── eksekusi.py                 # Script generate URL/token
├── input.txt                   # File bahan aktif (otomatis dibuat)
├── requirements.txt            # Python dependencies
├── README.md                   # Dokumentasi ini
├── LICENSE                     # Lisensi project
├── Bahan/                      # Folder menyimpan multiple file bahan
│   ├── bahan1.txt
│   ├── bahan2.txt
│   └── ...
├── data/                       # Folder data hasil generate
└── myenv/                      # Virtual environment Python
```

## 🔧 File Utama

| File | Deskripsi |
|------|-----------|
| `run.sh` | Launcher utama untuk Linux/Mac |
| `run.bat` | Launcher utama untuk Windows |
| `nf-token-generator.py` | Menu utama dengan CLI interface |
| `eksekusi.py` | Script untuk generate URL/token dari `input.txt` |
| `input.txt` | File bahan aktif (akan dibaca saat generate) |
| `Bahan/` | Folder untuk menyimpan banyak file bahan `.txt` |
| `myenv/` | Virtual environment Python (otomatis dibuat) |

## 🐛 Troubleshooting

### Error: Command 'python3' not found
**Solusi:** Install Python dari [python.org](https://www.python.org) atau gunakan package manager:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# Mac (dengan Homebrew)
brew install python3
```

### Error: Permission denied (run.sh)
**Solusi:** Berikan permission executable:
```bash
chmod +x run.sh
```

### Error: Module 'requests' not found
**Solusi:** Install dependencies:
```bash
pip install requests urllib3 playwright
```

### Chromium browser tidak terunduh (Desktop)
**Solusi:** Install manual:
```bash
# Aktifkan virtualenv terlebih dahulu
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows

# Install Chromium
python -m playwright install chromium
```

### Error: File 'input.txt' not found
**Solusi:** Jalankan mode "Ambil Bahan" terlebih dahulu sebelum generate URL

## 📝 Workflow Rekomendasi

1. **Persiapan Pertama Kali:**
   - Clone repository
   - Jalankan `run.sh` (akan setup otomatis)

2. **Workflow Harian:**
   - Jalankan `run.sh` → Pilih "1. Dapatkan Bahan" → Pilih "1. Ambil dari web" (atau "2. Ambil dari file tersimpan")
   - Setelah selesai, pilih "2. Generate URL"
   - Hasil tersimpan di file `input.txt` dan folder `data/`

3. **Kelola Multiple Bahan:**
   - Simpan file bahan di folder `Bahan/`
   - Gunakan mode "Ambil dari file tersimpan" untuk memilih file bahan

## 🤝 Kontribusi

Jika Anda menemukan bug atau memiliki saran, silakan buat **Issue** atau **Pull Request**.

## 📄 Lisensi

Project ini dilisensikan di bawah Lisensi MIT. Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

## ⚠️ Disclaimer

Project ini hanya untuk tujuan edukasi. Pengguna bertanggung jawab atas penggunaan tool ini. Pastikan sesuai dengan **Terms of Service** Netflix dan hukum yang berlaku di negara Anda.

Di HP/Android, submenu tetap tampil. Pilih `2. Ambil dari file tersimpan`.
Pilihan `1. Ambil dari web` akan ditolak karena membutuhkan
Playwright/Chromium desktop.

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

Mode ini khusus desktop/laptop karena membutuhkan Playwright dan Chromium.
Di HP/Android pilih `2. Ambil dari file tersimpan`.

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

Pilih `2. Dapatkan Bahan`, lalu pilih `2. Ambil dari file tersimpan`.

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

Desktop:

1. Masukkan banyak file bahan `.txt` ke folder `Bahan/`.
2. Jalankan `./run.sh`.
3. Pilih `2. Dapatkan Bahan`.
4. Pilih `2. Ambil dari file tersimpan`.
5. Pastikan program menampilkan pesan `Saved ... to input.txt`.
6. Kembali ke menu utama.
7. Pilih `1. Generate URL`.

HP/Termux:

1. Masukkan banyak file bahan `.txt` ke folder `Bahan/`.
2. Jalankan `sh run.sh --get-bahan-file`.
3. Pastikan program menampilkan pesan `Saved ... to input.txt`.
4. Jalankan `sh run.sh --generate`.

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

Ini hanya diperlukan untuk mode `Ambil dari web` di desktop/laptop.

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
