# Modifikasi Prelist/DSRT dari Kegiatan BPS

Tools untuk mengelola formulir survei dalam format PDF dengan QR code.

## 📋 Fitur Utama

- ✅ Menambahkan QR code ke formulir PDF
- ✅ Split PDF berdasarkan wilayah/marker
- ✅ Convert menjadi Excel (coming soon)

---

## 🚀 Tools Tersedia

### 1. **QR Code Generator** (`addQR.py`) ⭐

Generate dan embed QR code ke dalam PDF formulir.

**Fitur:**
- Flexible keyword search (mendukung "Identitas SLS", "Identitas Blok Sensus", dll)
- Auto-detect QR version berdasarkan ukuran data
- High error correction (30%)
- Detailed logging untuk debugging
- Case-insensitive search

**Cara Menggunakan:**
```bash
python3 addQR.py
```

**Output:** `namafile_qr.pdf`

---

### 2. **PDF Splitter** (`split_pdf_by_qr.py`) 📄

Split PDF besar menjadi file-file kecil berdasarkan marker "BLOK IV. CATATAN".

**Fitur:**
- Auto-detect semua marker dalam PDF
- Smart naming dari data QR
- Safe filename (karakter invalid otomatis dibersihkan)
- Duplicate handling (tambah suffix _1, _2, dst)
- GUI dialog untuk pilih folder output

**Cara Menggunakan:**
```bash
python3 split_pdf_by_qr.py
```

**Contoh Hasil:**
```
output_folder/
├── 97 0 6 YALIMO ALIMUHUK.pdf
├── 97 0 6 JAYAPURA DESA_X.pdf
└── 97 0 6 MERAUKE DESA_Y.pdf
```

---

### 3. **Debug & Testing Tools** 🔧

#### `debug_pdf_text.py` - Debug ekstraksi text
```bash
python3 debug_pdf_text.py
```
Lihat semua text yang diekstrak dari PDF, keyword yang ditemukan, dll.

#### `test_split.py` - Preview split tanpa membuat file
```bash
python3 test_split.py
```
Dry-run untuk lihat preview hasil split.

#### `test_extraction.py` - Test ekstraksi data QR
```bash
python3 test_extraction.py
```
Test ekstraksi data dengan sample data formulir.

#### `test_qr.py` - Test QR code sederhana
```bash
python3 test_qr.py
```
Generate QR code test sederhana untuk verify scanner.

---

## 📦 Installation

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- PyPDF2
- qrcode
- Pillow (PIL)
- PyMuPDF (fitz)
- tkinter (biasanya sudah include)

---

## 🔄 Workflow

### Scenario 1: PDF Gabung → Split + QR

1. **Split PDF:**
   ```bash
   python3 split_pdf_by_qr.py
   ```

2. **Generate QR untuk setiap file:**
   ```bash
   python3 addQR.py
   ```

### Scenario 2: PDF Terpisah → QR Saja

```bash
python3 addQR.py
```

### Scenario 3: Testing/Debug

1. **Cek ekstraksi text:**
   ```bash
   python3 debug_pdf_text.py
   ```

2. **Preview split:**
   ```bash
   python3 test_split.py
   ```

3. **Jalankan split:**
   ```bash
   python3 split_pdf_by_qr.py
   ```

---

## 🎯 Struktur Data QR Code

**Format:**
```
KODE_NUMERIK|NAMA_LOKASI
```

**Contoh:**
```
19720630204010512262001007000728|PAPUA|PEGUNUNGAN|YALIMO
```

**Data yang diekstrak:**
- Kode provinsi, kabupaten, kecamatan, desa
- Kode SLS/Sub-SLS
- Nomor kode sampel
- Nama lokasi

---

## 🛠️ Troubleshooting

### QR Code jadi "NO_DATA"
**Solusi:**
```bash
python3 debug_pdf_text.py
```
Cek apakah text berhasil diekstrak dan keyword ditemukan.

### Split tidak menemukan marker
**Solusi:**
```bash
python3 test_split.py
```
Preview untuk lihat apakah marker terdeteksi.

### QR Code tidak bisa di-scan
**Solusi:**
1. Pastikan QR minimal 2x2 cm saat dicetak
2. Test dengan `test_qr.py`
3. Cek data dengan `debug_pdf_text.py`

---

## 📁 File Structure

```
prelist/
├── addQR.py                    # QR generator
├── split_pdf_by_qr.py         # PDF splitter
├── debug_pdf_text.py          # Debug tool
├── test_split.py              # Split preview
├── test_extraction.py         # QR extraction test
├── test_qr.py                 # Simple QR test
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── README_SPLIT.md           # Detailed split docs
```

---

## 💡 Tips

### Custom QR Position
Edit `addQR.py` line 208:
```python
qr = {"size": 180, "x": 780, "y": 50}
```

### Custom Keywords
Edit `addQR.py` line 143-149 untuk keyword formulir lain:
```python
possible_keywords = [
    'Identitas Blok Sensus',
    'Identitas SLS',
    # Tambahkan keyword Anda
]
```

### Custom Error Correction
Edit `addQR.py` line 53:
```python
error_correction=qrcode.constants.ERROR_CORRECT_H  # High (30%)
```

Options: `ERROR_CORRECT_L` (7%), `ERROR_CORRECT_M` (15%), `ERROR_CORRECT_Q` (25%), `ERROR_CORRECT_H` (30%)

---

## 📚 Documentation

- **README_SPLIT.md** - Dokumentasi detail PDF splitter
- **PENJELASAN_ALUR.md** - Penjelasan alur data QR

---

## 📝 Changelog

### v1.0 (Current)
- ✅ Flexible keyword search
- ✅ High error correction QR
- ✅ PDF splitter dengan smart naming
- ✅ Debug tools lengkap
- ✅ Safe filename sanitization

---

**Last Updated:** 2026-01-21
