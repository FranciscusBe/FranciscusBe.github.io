"""
saw_engine.py
Engine perhitungan SAW (Simple Additive Weighting) untuk MEDISELECT.
Terpisah dari UI agar mudah diuji dan digunakan ulang.

FIXED: Normalisasi dan ranking dilakukan GLOBAL (seluruh kelas digabung),
sesuai sheet 'Perangkingan SAW (Seluruh Kelas)' di Excel.
"""

import re
from dataclasses import dataclass

import pandas as pd

# ─── Konfigurasi default ──────────────────────────────────────────────────────

BOBOT_DEFAULT: dict[str, float] = {
    "C1_PreTest": 0.15,
    "C2_Praktik": 0.35,
    "C3_PostTest": 0.20,
    "C4_Keaktifan": 0.15,
    "C5_Sikap": 0.15,
}

LABEL_KRITERIA: dict[str, str] = {
    "C1_PreTest": "C1 - Pre-Test",
    "C2_Praktik": "C2 - Praktik",
    "C3_PostTest": "C3 - Post-Test",
    "C4_Keaktifan": "C4 - Keaktifan",
    "C5_Sikap": "C5 - Sikap & Disiplin",
}

NILAI_MIN_LULUS: int = 70
MAKS_KRITERIA_DI_BAWAH: int = 1  # maksimal 1 kriteria boleh < 70
MIN_RATA_AMAN: int = 80  # rata-rata kriteria ≥ 70 harus ≥ 80

KOLOM_INPUT_WAJIB: list[str] = [
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

KOLOM_TEMPLATE: list[str] = [
    "No",
    "Nama Peserta",
    "Instansi",
    "Pelatihan",
    "Kelas",
    "C1 Pre-Test (15%)",
    "C2 Praktik (35%)",
    "C3 Post-Test (20%)",
    "C4 Keaktifan (15%)",
    "C5 Sikap & Disiplin (15%)",
]

# Alias nama kolom — toleran terhadap variasi header CSV
ALIAS_KOLOM: dict[str, list[str]] = {
    "Nama Peserta": ["Nama Peserta", "Nama"],
    "Instansi": ["Instansi"],
    "Pelatihan": ["Pelatihan"],
    "Kelas": ["Kelas"],
    "C1_PreTest": ["C1_PreTest", "C1 Pre-Test (15%)", "C1 Pre-Test", "Pre-Test", "C1"],
    "C2_Praktik": ["C2_Praktik", "C2 Praktik (35%)", "C2 Praktik", "Praktik", "C2"],
    "C3_PostTest": [
        "C3_PostTest",
        "C3 Post-Test (20%)",
        "C3 Post-Test",
        "Post-Test",
        "C3",
    ],
    "C4_Keaktifan": [
        "C4_Keaktifan",
        "C4 Keaktifan (15%)",
        "C4 Keaktifan",
        "Keaktifan",
        "C4",
    ],
    "C5_Sikap": [
        "C5_Sikap",
        "C5 Sikap & Disiplin (15%)",
        "C5 Sikap dan Disiplin (15%)",
        "C5 Sikap & Disiplin",
        "C5 Sikap dan Disiplin",
        "Sikap & Disiplin",
        "Sikap dan Disiplin",
        "C5",
    ],
}

KOLOM_OUTPUT: list[str] = [
    "No Urut",
    "Nama Peserta",
    "Instansi",
    "Pelatihan",
    "Kelas",
    "C1_PreTest",
    "C2_Praktik",
    "C3_PostTest",
    "C4_Keaktifan",
    "C5_Sikap",
    "N-C1",
    "N-C2",
    "N-C3",
    "N-C4",
    "N-C5",
    "W*C1",
    "W*C2",
    "W*C3",
    "W*C4",
    "W*C5",
    "Nilai SAW",
    "Peringkat",
    "Status",
]


# ─── Data class hasil ────────────────────────────────────────────────────────


@dataclass
class HasilSAW:
    df_hasil: pd.DataFrame
    df_normalisasi: pd.DataFrame
    df_terbobot: pd.DataFrame
    bobot: dict[str, float]
    ringkasan: dict
    pesan_error: str = ""
    sukses: bool = True


# ─── Normalisasi nama kolom ───────────────────────────────────────────────────


def _norm_teks(teks: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(teks).strip().lower())


def standarkan_kolom(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.map(lambda c: str(c).strip())
    peta = {_norm_teks(a): std for std, aliases in ALIAS_KOLOM.items() for a in aliases}
    rename_map = {c: peta[_norm_teks(c)] for c in df.columns if _norm_teks(c) in peta}
    return df.rename(columns=rename_map)


# ─── Validasi ─────────────────────────────────────────────────────────────────


def validasi_df(df: pd.DataFrame) -> pd.DataFrame:
    df = standarkan_kolom(df)

    hilang = [k for k in KOLOM_INPUT_WAJIB if k not in df.columns]
    if hilang:
        kolom_output_lama = {"N-C1", "N-C2", "Nilai SAW", "Peringkat", "Status"}
        if kolom_output_lama.intersection(df.columns):
            raise ValueError(
                "File terdeteksi sebagai OUTPUT hasil perhitungan, bukan INPUT data mentah. "
                "Gunakan file input dengan nilai asli peserta."
            )
        raise ValueError(
            f"Kolom berikut tidak ditemukan: {hilang}. "
            "Pastikan header CSV sesuai template."
        )

    df = df[KOLOM_INPUT_WAJIB].copy()  # type: ignore[assignment]
    kriteria = list(BOBOT_DEFAULT)
    for k in kriteria:
        df[k] = pd.to_numeric(df[k], errors="coerce")

    baris_na = df[df[kriteria].isna().any(axis=1)]
    if not baris_na.empty:
        raise ValueError(
            f"Terdapat nilai kosong atau bukan angka pada {len(baris_na)} baris: "
            f"{baris_na['Nama Peserta'].tolist()}"
        )

    return df


# ─── Perhitungan SAW ──────────────────────────────────────────────────────────


def _hitung_saw_global(df: pd.DataFrame, bobot: dict[str, float]) -> pd.DataFrame:
    """
    Normalisasi dan ranking dilakukan secara GLOBAL (seluruh kelas digabung).
    MAX diambil dari seluruh dataset — sesuai Excel sheet 'Perangkingan SAW (Seluruh Kelas)'.
    Formula: N-Ci = x_ij / MAX(x_ij) dimana MAX dihitung dari semua peserta semua kelas.
    """
    hasil = df.copy()
    kriteria = list(bobot)
    hasil["_urut_asli"] = range(len(hasil))

    # MAX global dari seluruh dataset (bukan per kelas)
    max_val = hasil[kriteria].max()

    for k in kriteria:
        kode = k.split("_")[0]
        hasil[f"N-{kode}"] = hasil[k] / max_val[k]
        hasil[f"W*{kode}"] = hasil[f"N-{kode}"] * bobot[k]

    kolom_terbobot = [f"W*{k.split('_')[0]}" for k in kriteria]
    hasil["Nilai SAW"] = hasil[kolom_terbobot].sum(axis=1)

    hasil["Status"] = ""

    nilai_kriteria = hasil[kriteria]
    di_bawah_60 = nilai_kriteria.lt(NILAI_MIN_LULUS).sum(axis=1)

    # Hitung rata-rata hanya dari kriteria yang >= batas
    nilai_ge = nilai_kriteria.where(nilai_kriteria >= NILAI_MIN_LULUS, 0)
    jumlah_ge = nilai_kriteria.ge(NILAI_MIN_LULUS).sum(axis=1).replace(0, 1)
    rata_ge = (nilai_ge.sum(axis=1) / jumlah_ge).round(2)

    lulus = (di_bawah_60 <= MAKS_KRITERIA_DI_BAWAH) & (rata_ge >= MIN_RATA_AMAN)
    hasil["Status"] = lulus.map({True: "LULUS", False: "TIDAK LULUS"})  # type: ignore[union-attr]

    # Sort: LULUS dulu (Nilai SAW desc, Nama asc), lalu TIDAK LULUS (urut asli)
    lulus_df = hasil[hasil["Status"] == "LULUS"].sort_values(
        ["Nilai SAW", "Nama Peserta"],
        ascending=[False, True],  # type: ignore[call-overload]
    )
    tidak_lulus_df = hasil[hasil["Status"] == "TIDAK LULUS"].sort_values("_urut_asli")  # type: ignore[call-overload]

    hasil = pd.concat([lulus_df, tidak_lulus_df], ignore_index=True)
    hasil["Peringkat"] = ""
    mask = hasil["Status"] == "LULUS"
    peringkat_vals = [str(i) for i in range(1, int(mask.sum()) + 1)]
    hasil.loc[mask, "Peringkat"] = peringkat_vals
    hasil.insert(0, "No Urut", list(range(1, len(hasil) + 1)))  # type: ignore[arg-type]

    return hasil.drop(columns="_urut_asli")


def hitung_saw(df: pd.DataFrame, bobot: dict[str, float] | None = None) -> HasilSAW:
    if bobot is None:
        bobot = BOBOT_DEFAULT.copy()

    total_bobot = sum(bobot.values())
    if abs(total_bobot - 1.0) > 0.001:
        return HasilSAW(
            df_hasil=pd.DataFrame(),
            df_normalisasi=pd.DataFrame(),
            df_terbobot=pd.DataFrame(),
            bobot=bobot,
            ringkasan={},
            pesan_error=f"Total bobot harus 1.0, saat ini {total_bobot:.4f}.",
            sukses=False,
        )

    try:
        df_valid = validasi_df(df)
    except ValueError as exc:
        return HasilSAW(
            df_hasil=pd.DataFrame(),
            df_normalisasi=pd.DataFrame(),
            df_terbobot=pd.DataFrame(),
            bobot=bobot,
            ringkasan={},
            pesan_error=str(exc),
            sukses=False,
        )

    # FIXED: Ranking global — semua kelas digabung, MAX diambil dari seluruh data
    df_hasil = _hitung_saw_global(df_valid, bobot)
    df_hasil = df_hasil[KOLOM_OUTPUT]

    kolom_normalisasi = [
        "No Urut",
        "Nama Peserta",
        "Instansi",
        "Pelatihan",
        "Kelas",
        "N-C1",
        "N-C2",
        "N-C3",
        "N-C4",
        "N-C5",
        "Status",
    ]
    kolom_terbobot = [
        "No Urut",
        "Nama Peserta",
        "Instansi",
        "Pelatihan",
        "Kelas",
        "W*C1",
        "W*C2",
        "W*C3",
        "W*C4",
        "W*C5",
        "Nilai SAW",
        "Peringkat",
        "Status",
    ]

    total = len(df_hasil)
    lulus = int((df_hasil["Status"] == "LULUS").sum())

    ringkasan = {
        "total_peserta": total,
        "total_lulus": lulus,
        "total_tidak_lulus": total - lulus,
        "rata_rata_saw": round(df_hasil["Nilai SAW"].mean(), 6),
        "nilai_saw_tertinggi": round(df_hasil["Nilai SAW"].max(), 6),
        "nilai_saw_terendah": round(df_hasil["Nilai SAW"].min(), 6),
        "pelatihan_list": list(df_hasil["Pelatihan"].unique()),  # type: ignore[union-attr]
        "kelas_list": list(df_hasil["Kelas"].unique()),  # type: ignore[union-attr]
    }

    return HasilSAW(
        df_hasil=df_hasil.round(6),  # type: ignore[arg-type]
        df_normalisasi=df_hasil[kolom_normalisasi].round(6),  # type: ignore[arg-type]
        df_terbobot=df_hasil[kolom_terbobot].round(6),  # type: ignore[arg-type]
        bobot=bobot,
        ringkasan=ringkasan,
        sukses=True,
    )


def buat_template_csv() -> pd.DataFrame:
    return pd.DataFrame(columns=KOLOM_TEMPLATE)  # type: ignore[arg-type]
