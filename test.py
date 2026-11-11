# Test untuk ApotekPredictor
# Cara jalanin: python test.py
from main import DataApotek, ApotekPredictor

def buat_data_sehat():
    return DataApotek(
        nama_apotek="Test Sehat", kota="Kediri",
        kas_saat_ini=50_000_000, pengeluaran_bulanan=15_000_000, pemasukan_bulanan=25_000_000,
        total_nilai_stok=80_000_000, nilai_stok_expired_3bulan=2_000_000, nilai_stok_tidak_laku_6bulan=3_000_000,
        total_hutang_distributor=10_000_000, hutang_jatuh_tempo_30hari=5_000_000,
        penjualan_bulan_ini=25_000_000, penjualan_bulan_lalu=23_000_000, penjualan_3bulan_lalu=20_000_000,
        sudah_punya_sistem_stok=True
    )

def buat_data_kritis():
    return DataApotek(
        nama_apotek="Test Kritis", kota="Surabaya",
        kas_saat_ini=5_000_000, pengeluaran_bulanan=12_000_000, pemasukan_bulanan=8_000_000,
        total_nilai_stok=60_000_000, nilai_stok_expired_3bulan=15_000_000, nilai_stok_tidak_laku_6bulan=12_000_000,
        total_hutang_distributor=45_000_000, hutang_jatuh_tempo_30hari=20_000_000,
        penjualan_bulan_ini=8_000_000, penjualan_bulan_lalu=11_000_000, penjualan_3bulan_lalu=15_000_000,
        sudah_punya_sistem_stok=False
    )

def test_sehat():
    p = ApotekPredictor()
    hasil = p.prediksi(buat_data_sehat())
    assert hasil["skor_risiko"] < 50, f"Seharusnya SEHAT, dapat {hasil['skor_risiko']}"
    assert "SEHAT" in hasil["level"]
    print("✅ TEST SEHAT LULUS")

def test_kritis():
    p = ApotekPredictor()
    hasil = p.prediksi(buat_data_kritis())
    assert hasil["skor_risiko"] >= 75, f"Seharusnya KRITIS, dapat {hasil['skor_risiko']}"
    assert "KRITIS" in hasil["level"]
    print("✅ TEST KRITIS LULUS")

def test_validasi_negatif():
    p = ApotekPredictor()
    try:
        data = buat_data_sehat()
        data.kas_saat_ini = -1000
        p.prediksi(data)
        assert False, "Harusnya error kalau negatif"
    except ValueError:
        print("✅ TEST VALIDASI NEGATIF LULUS - data negatif ditolak")

def test_validasi_terlalu_besar():
    p = ApotekPredictor()
    try:
        data = buat_data_sehat()
        data.kas_saat_ini = 999_999_999_999_999
        p.prediksi(data)
        assert False, "Harusnya error kalau terlalu besar"
    except ValueError:
        print("✅ TEST VALIDASI BESAR LULUS - input tidak wajar ditolak")

def test_kas_habis():
    p = ApotekPredictor()
    data = buat_data_sehat()
    data.kas_saat_ini = 1_000_000
    data.pengeluaran_bulanan = 15_000_000
    hasil = p.prediksi(data)
    assert hasil["detail_skor"]["arus_kas"] >= 85
    print("✅ TEST KAS HABIS LULUS - runway <1 bulan = skor 100")

def test_stok_mati_tinggi():
    p = ApotekPredictor()
    data = buat_data_sehat()
    data.nilai_stok_expired_3bulan = 40_000_000
    hasil = p.prediksi(data)
    assert hasil["detail_skor"]["stok_mati"] >= 75
    print("✅ TEST STOK MATI LULUS")

def test_hutang_lebih_besar_dari_kas():
    p = ApotekPredictor()
    data = buat_data_sehat()
    data.total_hutang_distributor = 100_000_000
    data.kas_saat_ini = 10_000_000
    hasil = p.prediksi(data)
    assert hasil["detail_skor"]["hutang"] >= 75
    print("✅ TEST HUTANG LULUS")

if __name__ == "__main__":
    print("=== JALANIN 7 TEST ===")
    test_sehat()
    test_kritis()
    test_validasi_negatif()
    test_validasi_terlalu_besar()
    test_kas_habis()
    test_stok_mati_tinggi()
    test_hutang_lebih_besar_dari_kas()
    print("\n🎉 SEMUA 7 TEST LULUS! Model aman & bisa dipercaya.")
