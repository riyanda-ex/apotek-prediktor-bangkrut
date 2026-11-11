# Cara Berkontribusi

Terima kasih mau bantu apotek di Indonesia jadi lebih sehat!

## Cara Cepat

1. Fork repo ini
2. Buat branch baru: `git checkout -b fitur-nama-fitur`
3. Ubah kode + tambah test di `test.py`
4. Pastikan semua test lulus: `python test.py`
5. Buat Pull Request dengan penjelasan jelas

## Aturan

- Jangan ubah `config.json` tanpa alasan jelas di PR
- Semua fitur baru WAJIB ada test-nya
- Jangan masukkan data apotek asli / data pasien
- Gunakan Bahasa Indonesia yang sopan di komentar kode
- Satu PR = satu fitur saja, jangan dicampur

## Contoh PR yang Bagus

Judul: `Tambah deteksi stok mendekati expired 7 hari`

Isi: `Menambah peringatan dini untuk stok yang expired < 7 hari, karena sebelumnya hanya 3 bulan. Sudah ditambah test baru.`

## Pertanyaan?

Buka tab Issues, buat issue baru dengan judul yang jelas.
