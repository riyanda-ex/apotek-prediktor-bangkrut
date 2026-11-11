# Kebijakan Keamanan

## Versi yang Didukung

| Versi | Didukung |
|-------|----------|
| 3.x (terbaru) | ✅ |
| < 3.0 | ❌ |

Selalu gunakan versi terbaru di branch `main`.

## Cara Melaporkan Bug Keamanan

**JANGAN** buat Issue publik untuk bug keamanan.

Caranya:
1. Buka tab **Security** di repo ini
2. Klik **Report a vulnerability**
3. Jelaskan bug-nya, langkah reproduksi, dan dampaknya

Atau hubungi pemilik repo lewat GitHub profile.

Kami akan merespon dalam **48 jam** dan memperbaiki dalam **7 hari** jika terbukti valid.

## Hal yang Dijamin Aman di Proyek Ini

- Tidak ada data pasien / NIK / KTP yang disimpan
- Semua data diproses lokal (offline), tidak dikirim ke server
- Tidak ada API key / password di dalam kode
- Input divalidasi - angka negatif / tidak wajar ditolak

## Yang Bukan Bug Keamanan

- Skor prediksi tidak 100% akurat - ini alat bantu edukasi, bukan nasihat keuangan
- Perbedaan hasil karena beda `config.json` - itu disengaja, config bisa diubah

Terima kasih sudah membantu membuat proyek ini lebih aman.
