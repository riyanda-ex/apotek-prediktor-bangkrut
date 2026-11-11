![Tests](https://github.com/riyanda-ex/apotek-prediktor-bangkrut/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-All_Rights_Reserved-red.svg)
![Standard](https://img.shields.io/badge/Standard-ISO_31000-green.svg)
![Explainable AI](https://img.shields.io/badge/AI-Explainable-orange.svg)

# Apotek Prediktor Bangkrut

Prediksi risiko kebangkrutan apotek di Indonesia sejak dini, dengan penjelasan yang bisa dipahami pemilik apotek - bukan sekadar angka.

Dibangun dengan pendekatan **Explainable AI** dan standar manajemen risiko **ISO 31000**.

> ⚠️ **Disclaimer:** Ini alat bantu edukasi, bukan nasihat keuangan. Selalu verifikasi dengan akuntan / konsultan UMKM.

---

## Kenapa Proyek Ini Ada?

Banyak apotek tutup bukan karena tidak laku, tapi karena:
- Kas habis padahal stok menumpuk di gudang
- Hutang ke distributor menumpuk diam-diam
- Penjualan turun pelan-pelan tanpa disadari
- Tidak ada sistem peringatan dini

Proyek ini memberi peringatan **3 bulan sebelum** apotek benar-benar kritis.

## Fitur Utama

- **Skor Risiko 0-100** - dari 5 faktor: Arus Kas, Stok Mati, Hutang, Penjualan, Operasional
- **Level Risiko** - SEHAT / WASPADA / BAHAYA / KRITIS
- **Alasan yang Jelas** - setiap skor dijelaskan kenapa naik, bukan kotak hitam
- **Rekomendasi Aksi** - langkah nyata yang bisa langsung dilakukan
- **100% Offline** - tidak ada data yang dikirim ke server, privasi aman
- **Config Bisa Diubah** - semua ambang batas ada di `config.json`

## Cara Pakai - 1 Menit

1. Pastikan Python 3.9+ sudah terinstall
2. Download / clone repo ini
3. Jalankan:
```bash
python main.py
