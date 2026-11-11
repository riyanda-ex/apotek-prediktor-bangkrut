"""
Apotek Prediktor Bangkrut - v3 International Standard

Prediksi risiko kebangkrutan apotek 3 bulan ke depan
berdasarkan 5 pilar kesehatan finansial apotek.

Model: Rule-Based Scoring + Weighted Risk (Explainable AI)
Bukan Black-Box. Semua skor bisa dijelaskan ke pemilik apotek.

STANDAR:
- ISO 31000 Risk Management
- Explainable AI (XAI) - setiap skor ada alasannya
- No PII - tidak menyimpan nama pasien / data sensitif

DISCLAIMER: Ini alat bantu edukasi finansial, BUKAN nasihat
keuangan / investasi. Keputusan tetap di pemilik apotek + akuntan.
"""

import json
import os
from datetime import datetime, date
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# ================= CONFIG - BISA DIUBAH TANPA UBAH KODE =================
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

DEFAULT_CONFIG = {
    "bobot": {
        "arus_kas": 0.30,      # Paling penting: apotek mati karena kehabisan kas
        "stok_mati": 0.25,     # Stok expired / tidak laku
        "hutang": 0.20,        # Hutang ke distributor / PBF
        "penjualan": 0.15,     # Tren penjualan turun
        "operasional": 0.10    # Biaya sewa, gaji, listrik
    },
    "threshold": {
        "kritis": 75,   # >=75 = KRITIS, kemungkinan bangkrut <3 bulan
        "waspada": 50,  # 50-74 = WASPADA
        "sehat": 0      # <50 = SEHAT
    }
}

# ================= DATA MODEL =================
@dataclass
class DataApotek:
    nama_apotek: str
    kota: str
    # 1. Arus Kas (Cash Flow)
    kas_saat_ini: float  # Rupiah di kas + rekening
    pengeluaran_bulanan: float # Sewa + gaji + listrik + dll
    pemasukan_bulanan: float

    # 2. Stok
    total_nilai_stok: float
    nilai_stok_expired_3bulan: float # Stok yang akan expired <3 bulan
    nilai_stok_tidak_laku_6bulan: float # Stok tidak terjual 6 bulan

    # 3. Hutang
    total_hutang_distributor: float
    hutang_jatuh_tempo_30hari: float

    # 4. Penjualan
    penjualan_bulan_ini: float
    penjualan_bulan_lalu: float
    penjualan_3bulan_lalu: float

    # 5. Operasional
    jumlah_karyawan: int = 2
    sudah_punya_sistem_stok: bool = False

    def validate(self):
        """Validasi input - mencegah data aneh / negatif / manipulasi"""
        for field_name in ["kas_saat_ini", "pengeluaran_bulanan", "pemasukan_bulanan",
                           "total_nilai_stok", "nilai_stok_expired_3bulan",
                           "nilai_stok_tidak_laku_6bulan", "total_hutang_distributor",
                           "hutang_jatuh_tempo_30hari", "penjualan_bulan_ini",
                           "penjualan_bulan_lalu", "penjualan_3bulan_lalu"]:
            val = getattr(self, field_name)
            if val < 0:
                raise ValueError(f"{field_name} tidak boleh negatif: {val}")
            if val > 100_000_000_000: # >100 Miliar, kemungkinan salah input
                raise ValueError(f"{field_name} terlalu besar, cek input: {val}")
        if self.pengeluaran_bulanan == 0:
            raise ValueError("pengeluaran_bulanan tidak boleh 0")
        return True

# ================= PREDICTOR =================
class ApotekPredictor:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.bobot = self.config["bobot"]
        self.threshold = self.config["threshold"]

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return DEFAULT_CONFIG

    def _hitung_skor_arus_kas(self, d: DataApotek) -> tuple[int, List[str]]:
        """Skor 0-100, makin tinggi makin bahaya"""
        alasan = []
        # Runway = berapa bulan bisa bertahan tanpa pemasukan
        runway = d.kas_saat_ini / d.pengeluaran_bulanan if d.pengeluaran_bulanan > 0 else 0

        if runway < 1:
            skor = 100
            alasan.append(f"CRITICAL: Kas hanya cukup {runway:.1f} bulan. Apotek bisa tutup bulan depan.")
        elif runway < 2:
            skor = 85
            alasan.append(f"Kas hanya cukup {runway:.1f} bulan. Darurat.")
        elif runway < 3:
            skor = 65
            alasan.append(f"Kas cukup {runway:.1f} bulan. Harus segera cari pemasukan.")
        elif runway < 6:
            skor = 35
            alasan.append(f"Kas cukup {runway:.1f} bulan. Masih aman tapi tipis.")
        else:
            skor = 10
            alasan.append(f"Kas aman, cukup {runway:.1f} bulan.")

        # Arus kas negatif
        if d.pemasukan_bulanan < d.pengeluaran_bulanan:
            skor = min(100, skor + 20)
            selisih = d.pengeluaran_bulanan - d.pemasukan_bulanan
            alasan.append(f"RUGI bulanan Rp {selisih:,.0f}. Keluar lebih besar dari masuk.")

        return skor, alasan

    def _hitung_skor_stok(self, d: DataApotek) -> tuple[int, List[str]]:
        alasan = []
        if d.total_nilai_stok == 0:
            return 0, ["Tidak ada stok - apotek baru / tutup"]

        rasio_expired = d.nilai_stok_expired_3bulan / d.total_nilai_stok
        rasio_mati = d.nilai_stok_tidak_laku_6bulan / d.total_nilai_stok
        rasio_total_mati = rasio_expired + rasio_mati

        if rasio_total_mati > 0.40:
            skor = 95
            alasan.append(f"{rasio_total_mati*100:.1f}% stok adalah stok mati / expired. Uang terjebak di gudang.")
        elif rasio_total_mati > 0.25:
            skor = 75
            alasan.append(f"{rasio_total_mati*100:.1f}% stok mati. Segera obral / retur ke distributor.")
        elif rasio_total_mati > 0.15:
            skor = 50
            alasan.append(f"{rasio_total_mati*100:.1f}% stok mati. Mulai bersihkan stok.")
        elif rasio_total_mati > 0.05:
            skor = 25
            alasan.append(f"{rasio_total_mati*100:.1f}% stok mati. Masih wajar.")
        else:
            skor = 5
            alasan.append(f"Stok sehat, hanya {rasio_total_mati*100:.1f}% stok mati.")

        return skor, alasan

    def _hitung_skor_hutang(self, d: DataApotek) -> tuple[int, List[str]]:
        alasan = []
        if d.total_hutang_distributor == 0:
            return 5, ["Tidak ada hutang. Sangat sehat."]
        # Debt to Cash Ratio
        ratio = d.total_hutang_distributor / d.kas_saat_ini if d.kas_saat_ini > 0 else 999
        if ratio > 3:
            skor = 95
            alasan.append(f"Hutang {ratio:.1f}x lipat dari kas. Distributor bisa stop kirim obat.")
        elif ratio > 2:
            skor = 75
            alasan.append(f"Hutang {ratio:.1f}x lipat dari kas. Sangat berat.")
        elif ratio > 1:
            skor = 55
            alasan.append(f"Hutang lebih besar dari kas. Harus negosiasi cicilan.")
        elif ratio > 0.5:
            skor = 30
            alasan.append(f"Hutang {ratio:.1f}x kas. Masih terkendali.")
        else:
            skor = 10
            alasan.append(f"Hutang ringan, {ratio:.1f}x kas.")

        if d.hutang_jatuh_tempo_30hari > d.kas_saat_ini:
            skor = 100
            alasan.append(f"CRITICAL: Hutang jatuh tempo 30 hari Rp {d.hutang_jatuh_tempo_30hari:,.0f} > kas Rp {d.kas_saat_ini:,.0f}. Gagal bayar!")

        return skor, alasan

    def _hitung_skor_penjualan(self, d: DataApotek) -> tuple[int, List[str]]:
        alasan = []
        if d.penjualan_3bulan_lalu == 0:
            return 20, ["Data penjualan 3 bulan lalu kosong - apotek baru"]
        tren = (d.penjualan_bulan_ini - d.penjualan_3bulan_lalu) / d.penjualan_3bulan_lalu
        if tren < -0.30:
            skor = 90
            alasan.append(f"Penjualan TURUN {abs(tren)*100:.1f}% dalam 3 bulan. Pelanggan kabur.")
        elif tren < -0.15:
            skor = 70
            alasan.append(f"Penjualan turun {abs(tren)*100:.1f}%. Cek kompetitor / harga.")
        elif tren < -0.05:
            skor = 45
            alasan.append(f"Penjualan turun tipis {abs(tren)*100:.1f}%.")
        elif tren < 0.05:
            skor = 25
            alasan.append(f"Penjualan stagnan {tren*100:.1f}%.")
        else:
            skor = 5
            alasan.append(f"Penjualan NAIK {tren*100:.1f}%. Bagus!")
        return skor, alasan

    def _hitung_skor_operasional(self, d: DataApotek) -> tuple[int, List[str]]:
        alasan = []
        # Biaya operasional / pemasukan
        if d.pemasukan_bulanan == 0:
            return 80, ["Tidak ada pemasukan bulan ini."]
        rasio_biaya = d.pengeluaran_bulanan / d.pemasukan_bulanan
        if rasio_biaya > 0.95:
            skor = 90
            alasan.append(f"Biaya {rasio_biaya*100:.1f}% dari pemasukan. Hampir tidak ada untung.")
        elif rasio_biaya > 0.85:
            skor = 65
            alasan.append(f"Biaya {rasio_biaya*100:.1f}% dari pemasukan. Margin sangat tipis.")
        elif rasio_biaya > 0.70:
            skor = 40
            alasan.append(f"Biaya {rasio_biaya*100:.1f}% dari pemasukan. Normal untuk apotek kecil.")
        else:
            skor = 15
            alasan.append(f"Biaya {rasio_biaya*100:.1f}% dari pemasukan. Efisien.")
        if not d.sudah_punya_sistem_stok:
            skor = min(100, skor + 10)
            alasan.append("Belum ada sistem stok digital - rawan stok mati tidak ketahuan.")
        return skor, alasan

    def prediksi(self, d: DataApotek) -> Dict:
        d.validate()
        skor_detail = {}
        semua_alasan = []

        funcs = {
            "arus_kas": self._hitung_skor_arus_kas,
            "stok_mati": self._hitung_skor_stok,
            "hutang": self._hitung_skor_hutang,
            "penjualan": self._hitung_skor_penjualan,
            "operasional": self._hitung_skor_operasional,
        }
        for nama, func in funcs.items():
            skor, alasan = func(d)
            skor_detail[nama] = skor
            semua_alasan.extend(alasan)

        # Skor akhir = weighted average
        skor_akhir = sum(skor_detail[k] * self.bobot[k] for k in skor_detail)

        if skor_akhir >= self.threshold["kritis"]:
            level = "KRITIS 🔴"
            prediksi_text = "Risiko TINGGI bangkrut dalam < 3 bulan jika tidak ada tindakan"
            rekomendasi = [
                "1. SEGERA negosiasi hutang ke distributor - minta perpanjangan tempo 60 hari",
                "2. Obral stok hampir expired (diskon 30-50%) - ubah stok jadi kas",
                "3. Potong biaya tidak penting - jam buka, listrik, langganan",
                "4. Hubungi akuntan / konsultan UMKM terdekat HARI INI",
                "5. JANGAN ambil hutang baru untuk bayar hutang lama",
            ]
        elif skor_akhir >= self.threshold["waspada"]:
            level = "WASPADA 🟡"
            prediksi_text = "Risiko SEDANG - masih bisa diselamatkan dalam 3-6 bulan"
            rekomendasi = [
                "1. Bersihkan stok mati - retur ke PBF atau jual paket bundling",
                "2. Naikkan penjualan - layanan antar, kerjasama klinik terdekat",
                "3. Buat laporan kas harian - jangan sampai runway < 2 bulan",
                "4. Evaluasi harga - jangan perang harga dengan apotek jaringan",
            ]
        else:
            level = "SEHAT 🟢"
            prediksi_text = "Risiko RENDAH - apotek sehat, fokus tumbuh"
            rekomendasi = [
                "1. Pertahankan runway kas > 6 bulan",
                "2. Investasi ke sistem stok digital",
                "3. Tambah layanan: cek tensi gratis, konsultasi obat",
                "4. Sisihkan 10% laba untuk dana darurat",
            ]

        hasil = {
            "apotek": d.nama_apotek,
            "kota": d.kota,
            "tanggal_analisa": datetime.now().strftime("%d %B %Y %H:%M"),
            "skor_risiko": round(skor_akhir, 1),
            "level": level,
            "prediksi": prediksi_text,
            "detail_skor": skor_detail,
            "alasan": semua_alasan,
            "rekomendasi": rekomendasi,
            "disclaimer": "Alat bantu edukasi, bukan nasihat keuangan. Verifikasi dengan akuntan."
        }
        return hasil

    def tampilkan(self, hasil: Dict):
        print("\n" + "="*60)
        print(f"🏥 LAPORAN KESEHATAN APOTEK: {hasil['apotek']} - {hasil['kota']}")
        print(f"📅 {hasil['tanggal_analisa']}")
        print("="*60)
        print(f"SKOR RISIKO BANGKRUT: {hasil['skor_risiko']} / 100")
        print(f"LEVEL: {hasil['level']}")
        print(f"PREDIKSI: {hasil['prediksi']}")
        print("\n--- DETAIL 5 PILAR ---")
        for k, v in hasil['detail_skor'].items():
            print(f"  {k:<15}: {v}/100")
        print("\n--- KENAPA SKOR INI? (Explainable AI) ---")
        for a in hasil['alasan']:
            print(f"  • {a}")
        print("\n--- REKOMENDASI AKSI ---")
        for r in hasil['rekomendasi']:
            print(f"  {r}")
        print("\n⚠️ " + hasil['disclaimer'])
        print("="*60)

    def simpan_ke_json(self, hasil: Dict, folder: str = "laporan"):
        os.makedirs(folder, exist_ok=True)
        nama_file = f"{folder}/{hasil['apotek'].replace(' ', '_')}_{date.today()}.json"
        with open(nama_file, 'w', encoding='utf-8') as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Laporan tersimpan: {nama_file}")
        return nama_file

# ================= CONTOH PAKAI =================
if __name__ == "__main__":
    prediktor = ApotekPredictor()

    # CONTOH 1: Apotek Sehat
    apotek_sehat = DataApotek(
        nama_apotek="Apotek Sehat Jaya", kota="Kediri",
        kas_saat_ini=50_000_000, pengeluaran_bulanan=15_000_000, pemasukan_bulanan=25_000_000,
        total_nilai_stok=80_000_000, nilai_stok_expired_3bulan=2_000_000, nilai_stok_tidak_laku_6bulan=3_000_000,
        total_hutang_distributor=10_000_000, hutang_jatuh_tempo_30hari=5_000_000,
        penjualan_bulan_ini=25_000_000, penjualan_bulan_lalu=23_000_000, penjualan_3bulan_lalu=20_000_000,
        jumlah_karyawan=3, sudah_punya_sistem_stok=True
    )
    hasil1 = prediktor.prediksi(apotek_sehat)
    prediktor.tampilkan(hasil1)

    # CONTOH 2: Apotek Kritis
    apotek_kritis = DataApotek(
        nama_apotek="Apotek Harapan", kota="Surabaya",
        kas_saat_ini=5_000_000, pengeluaran_bulanan=12_000_000, pemasukan_bulanan=8_000_000,
        total_nilai_stok=60_000_000, nilai_stok_expired_3bulan=15_000_000, nilai_stok_tidak_laku_6bulan=12_000_000,
        total_hutang_distributor=45_000_000, hutang_jatuh_tempo_30hari=20_000_000,
        penjualan_bulan_ini=8_000_000, penjualan_bulan_lalu=11_000_000, penjualan_3bulan_lalu=15_000_000,
        jumlah_karyawan=2, sudah_punya_sistem_stok=False
    )
    hasil2 = prediktor.prediksi(apotek_kritis)
    prediktor.tampilkan(hasil2)
    prediktor.simpan_ke_json(hasil2)
