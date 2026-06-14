"""
test.py - Unit test untuk engine SAW
"""

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from saw_engine import (
    BOBOT_DEFAULT,
    KOLOM_INPUT_WAJIB,
    LABEL_KRITERIA,
    NILAI_MIN_LULUS,
    buat_template_csv,
    hitung_saw,
    validasi_df,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Konstanta
# ═══════════════════════════════════════════════════════════════════════════════


class TestKonstanta:
    def test_bobot_default_total_1(self):
        assert math.isclose(sum(BOBOT_DEFAULT.values()), 1.0)

    def test_label_kriteria_lengkap(self):
        for k in [
            "C1_PreTest",
            "C2_Praktik",
            "C3_PostTest",
            "C4_Keaktifan",
            "C5_Sikap",
        ]:
            assert k in LABEL_KRITERIA

    def test_nilai_min_lulus_valid(self):
        assert 0 < NILAI_MIN_LULUS <= 100

    def test_kolom_input_wajib_lengkap(self):
        expected = [
            "Nama Peserta",
            "Instansi",
            "Pelatihan",
            "Kelas",
            "C1_PreTest",
            "C2_Praktik",
            "C3_PostTest",
            "C4_Keaktifan",
            "C5_Sikap",
        ]
        assert KOLOM_INPUT_WAJIB == expected


# ═══════════════════════════════════════════════════════════════════════════════
# Template CSV
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateCSV:
    def test_template_ada_kolom(self):
        """Template CSV harus berupa DataFrame dengan kolom (walau kosong)."""
        tmpl = buat_template_csv()
        assert isinstance(tmpl, pd.DataFrame)
        assert len(tmpl.columns) >= 5  # minimal ada beberapa kolom
        # Kolom template pakai nama user-friendly, bukan KOLOM_INPUT_WAJIB
        assert "Nama Peserta" in tmpl.columns

    def test_template_kosong_aman(self):
        """Template awal tidak punya baris data (template kosong)."""
        tmpl = buat_template_csv()
        assert len(tmpl) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Validasi
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidasiDF:
    def _df_valid(self):
        return pd.DataFrame(
            {
                "No": [1, 2, 3],
                "Nama Peserta": ["Andi", "Budi", "Citra"],
                "Instansi": ["A", "B", "A"],
                "Pelatihan": ["X", "X", "X"],
                "Kelas": ["A", "A", "A"],
                "C1_PreTest": [80, 60, 90],
                "C2_Praktik": [70, 55, 85],
                "C3_PostTest": [90, 75, 95],
                "C4_Keaktifan": [85, 80, 70],
                "C5_Sikap": [75, 70, 80],
            }
        )

    def test_validasi_berhasil(self):
        df = validasi_df(self._df_valid())
        assert len(df) == 3
        for k in [
            "C1_PreTest",
            "C2_Praktik",
            "C3_PostTest",
            "C4_Keaktifan",
            "C5_Sikap",
        ]:
            assert pd.api.types.is_numeric_dtype(df[k])

    def test_validasi_kolom_kurang(self):
        df = pd.DataFrame({"Nama Peserta": ["A"], "C1_PreTest": [80]})
        with pytest.raises(ValueError, match="Kolom berikut tidak ditemukan"):
            validasi_df(df)

    def test_validasi_nilai_na(self):
        df = self._df_valid()
        df.loc[1, "C1_PreTest"] = None
        with pytest.raises(ValueError, match="nilai kosong"):
            validasi_df(df)

    def test_validasi_bilang_teks(self):
        df = self._df_valid()
        df["C2_Praktik"] = df["C2_Praktik"].astype(object)
        df.loc[1, "C2_Praktik"] = "abc"
        with pytest.raises(ValueError, match="nilai kosong"):
            validasi_df(df)


# ═══════════════════════════════════════════════════════════════════════════════
# hitung_saw
# ═══════════════════════════════════════════════════════════════════════════════


class TestHitungSAW:
    def _df_input(self):
        return pd.DataFrame(
            {
                "No": [1, 2, 3],
                "Nama Peserta": ["Andi", "Budi", "Citra"],
                "Instansi": ["A", "B", "A"],
                "Pelatihan": ["X", "X", "X"],
                "Kelas": ["A", "A", "A"],
                "C1_PreTest": [80, 60, 90],
                "C2_Praktik": [70, 55, 85],
                "C3_PostTest": [90, 75, 95],
                "C4_Keaktifan": [85, 80, 70],
                "C5_Sikap": [75, 70, 80],
            }
        )

    def test_bobot_tidak_1_gagal(self):
        bobot = {
            "C1_PreTest": 0.1,
            "C2_Praktik": 0.1,
            "C3_PostTest": 0.1,
            "C4_Keaktifan": 0.1,
            "C5_Sikap": 0.1,
        }
        hasil = hitung_saw(self._df_input(), bobot)
        assert not hasil.sukses
        assert "Total bobot" in hasil.pesan_error

    def test_hitung_sukses(self):
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        assert hasil.sukses
        assert hasil.pesan_error == ""

    def test_output_fields(self):
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        assert hasil.sukses

        # Ringkasan
        r = hasil.ringkasan
        assert r["total_peserta"] == 3
        assert r["total_lulus"] + r["total_tidak_lulus"] == 3
        assert 0 <= r["rata_rata_saw"] <= 1
        assert 0 <= r["nilai_saw_tertinggi"] <= 1
        assert 0 <= r["nilai_saw_terendah"] <= 1

        # DataFrame
        assert "Nilai SAW" in hasil.df_hasil.columns
        assert "Status" in hasil.df_hasil.columns
        assert len(hasil.df_normalisasi) == 3
        assert len(hasil.df_terbobot) == 3

    def test_nilai_saw_range(self):
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        assert hasil.sukses
        saw = hasil.df_hasil["Nilai SAW"]
        assert (saw >= 0).all()
        assert (saw <= 1).all()

    def test_status_valid(self):
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        assert hasil.sukses
        status = hasil.df_hasil["Status"].unique()
        for s in status:
            assert s in ("LULUS", "TIDAK LULUS")

    def test_peringkat_hanya_untuk_lulus(self):
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        df = hasil.df_hasil
        mask_lulus = df["Status"] == "LULUS"
        assert df.loc[mask_lulus, "Peringkat"].ne("").all()
        assert df.loc[~mask_lulus, "Peringkat"].eq("").all()

    def test_normalisasi_max_per_kelas(self):
        """N-C1..N-C5 dalam df_normalisasi, nilai max per kelas harus 1.0."""
        hasil = hitung_saw(self._df_input(), BOBOT_DEFAULT)
        assert hasil.sukses
        dfn = hasil.df_normalisasi
        for _, grp in dfn.groupby("Kelas"):
            for c in [f"N-C{i}" for i in range(1, 6)]:
                if c in grp.columns:
                    assert math.isclose(grp[c].max(), 1.0, rel_tol=1e-6)

    def test_bobot_custom(self):
        df = pd.DataFrame(
            {
                "No": [1, 2],
                "Nama Peserta": ["Andi", "Budi"],
                "Instansi": ["A", "B"],
                "Pelatihan": ["X", "X"],
                "Kelas": ["A", "A"],
                "C1_PreTest": [100, 50],
                "C2_Praktik": [100, 50],
                "C3_PostTest": [100, 50],
                "C4_Keaktifan": [100, 50],
                "C5_Sikap": [100, 50],
            }
        )
        bobot = {
            "C1_PreTest": 0.2,
            "C2_Praktik": 0.3,
            "C3_PostTest": 0.2,
            "C4_Keaktifan": 0.15,
            "C5_Sikap": 0.15,
        }
        hasil = hitung_saw(df, bobot)
        assert hasil.sukses
        assert (
            hasil.df_hasil.iloc[0]["Nilai SAW"] >= hasil.df_hasil.iloc[1]["Nilai SAW"]
        )
