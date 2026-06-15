"""
app.py
SPK - Sistem Penunjang Keputusan Seleksi Peserta Pelatihan Kesehatan
Berbasis Metode Simple Additive Weighting (SAW)
PT Cendekia Trust Integrity

Jalankan:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st

from charts import (
    chart_boxplot_kriteria,
    chart_instansi,
    chart_kontribusi_bobot,
    chart_radar_kriteria,
    chart_ranking_saw,
    chart_scatter_dua_kriteria,
)
from saw_engine import (
    BOBOT_DEFAULT,
    LABEL_KRITERIA,
    NILAI_MIN_LULUS,
    buat_template_csv,
    hitung_saw,
)

# ─── Konfigurasi halaman ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="SPK - SPK SAW",
    page_icon="assets/favicon.ico" if False else ":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS kustom ───────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Background utama */
    .stApp {
        background: #0a0f1e;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0d1526;
        border-right: 1px solid rgba(100,116,139,0.15);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 10px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }

    /* Tabs */
    [data-baseweb="tab-list"] {
        background: #111827;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(100,116,139,0.15);
    }
    [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #64748b !important;
        padding: 8px 16px !important;
    }
    [aria-selected="true"][data-baseweb="tab"] {
        background: #1e3a5f !important;
        color: #93c5fd !important;
    }

    /* Header app */
    .app-header {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 24px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(100,116,139,0.15);
    }
    .app-title {
        font-size: 22px;
        font-weight: 600;
        color: #e2e8f0;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }
    .app-subtitle {
        font-size: 12px;
        color: #475569;
        margin-top: 4px;
        font-weight: 400;
    }
    .badge-saw {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 0.08em;
        margin-top: 6px;
        border: 1px solid rgba(147,197,253,0.2);
    }

    /* Upload area */
    [data-testid="stFileUploadDropzone"] {
        background: #111827 !important;
        border: 1.5px dashed rgba(100,116,139,0.4) !important;
        border-radius: 10px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 8px;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: #111827;
        border: 1px solid rgba(100,116,139,0.15) !important;
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border-color: rgba(100,116,139,0.15);
    }

    /* Alert sukses */
    .stSuccess {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.25) !important;
        border-radius: 8px !important;
        color: #6ee7b7 !important;
    }
    .stError {
        background: rgba(220,38,38,0.08) !important;
        border: 1px solid rgba(220,38,38,0.25) !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background: rgba(245,158,11,0.08) !important;
        border: 1px solid rgba(245,158,11,0.25) !important;
        border-radius: 8px !important;
    }
    .stInfo {
        background: rgba(14,165,233,0.08) !important;
        border: 1px solid rgba(14,165,233,0.25) !important;
        border-radius: 8px !important;
    }

    /* Tabel hasil - warna status */
    .status-lulus { color: #4ade80; font-weight: 600; }
    .status-tidak { color: #f87171; font-weight: 600; }

    /* Section label */
    .section-label {
        font-size: 11px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }

    /* Rank badge */
    .rank-1 { color: #fbbf24; font-weight: 700; }
    .rank-2 { color: #9ca3af; font-weight: 600; }
    .rank-3 { color: #b45309; font-weight: 600; }

    /* Input number */
    input[type="number"] {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(100,116,139,0.3) !important;
        border-radius: 6px !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        background: #111827 !important;
        border-color: rgba(100,116,139,0.3) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0f1e; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }

    /* ── Tombol download ── */
    [data-testid="stDownloadButton"] button {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(100,116,139,0.3) !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: border-color 0.15s, background 0.15s;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #1e3a5f !important;
        border-color: #3b82f6 !important;
        color: #93c5fd !important;
    }

    /* ── Tombol umum ── */
    [data-testid="stButton"] button {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(100,116,139,0.3) !important;
        border-radius: 8px !important;
    }
    [data-testid="stButton"] button:hover {
        background: #1e3a5f !important;
        border-color: #3b82f6 !important;
        color: #93c5fd !important;
    }

    /* ── Radio button ── */
    [data-testid="stRadio"] label {
        color: #94a3b8 !important;
        font-size: 13px !important;
    }
    /* lingkaran luar */
    [data-testid="stRadio"] [data-baseweb="radio"] div[class] {
        border-color: rgba(100,116,139,0.5) !important;
        background: transparent !important;
    }
    /* lingkaran dalam (dot) saat terpilih */
    [data-testid="stRadio"] [data-baseweb="radio"] input:checked ~ div {
        border-color: #3b82f6 !important;
        background: #3b82f6 !important;
    }
    /* label terpilih */
    [data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) label,
    [data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) p {
        color: #93c5fd !important;
        font-weight: 600 !important;
    }
    /* fallback: dot warna biru via ::before */
    [data-testid="stRadio"] [role="radio"][aria-checked="true"] ~ div::before,
    [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
        border-color: #3b82f6 !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] section {
        background: #111827 !important;
        border-color: rgba(100,116,139,0.3) !important;
    }
    [data-testid="stFileUploader"] button {
        background: #111827 !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(100,116,139,0.3) !important;
    }

    /* ── Number input ── */
    [data-testid="stNumberInput"] input {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border-color: rgba(100,116,139,0.3) !important;
    }
    [data-testid="stNumberInput"] button {
        background: #1a2535 !important;
        color: #94a3b8 !important;
        border-color: rgba(100,116,139,0.2) !important;
    }

    /* ── Selectbox dropdown ── */
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] ul {
        background: #111827 !important;
        border: 1px solid rgba(100,116,139,0.2) !important;
    }
    [data-baseweb="popover"] [role="option"] {
        background: #111827 !important;
        color: #e2e8f0 !important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {
        background: #1e3a5f !important;
        color: #93c5fd !important;
    }

    /* ── Expander content ── */
    [data-testid="stExpander"] > div > div {
        background: #0d1526 !important;
        color: #94a3b8 !important;
    }

    /* ── Caption / small text ── */
    [data-testid="stCaptionContainer"] p {
        color: #475569 !important;
    }

    /* ── Top white bar Streamlit deploy menu ── */
    [data-testid="stHeader"] {
        background: #0a0f1e !important;
        border-bottom: 1px solid rgba(100,116,139,0.1);
    }
    header[data-testid="stHeader"] {
        background: #0a0f1e !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ─── Helper ───────────────────────────────────────────────────────────────────


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def format_saw(val: float) -> str:
    return f"{val:.6f}"


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
    <div style="margin-bottom: 20px;">
        <div style="font-size:16px; font-weight:600; color:#e2e8f0;">SPK</div>
        <div style="font-size:11px; color:#475569; margin-top:2px;">SPK Seleksi Peserta Pelatihan</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Upload Data</div>', unsafe_allow_html=True)
    file_upload = st.file_uploader(
        "File CSV data peserta",
        type=["csv"],
        help="Format: kolom nama peserta, instansi, pelatihan, kelas, C1-C5",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<div class="section-label">Konfigurasi Bobot Kriteria</div>',
        unsafe_allow_html=True,
    )
    st.caption("Total bobot harus = 1.0")

    bobot_input: dict[str, float] = {}
    for kode, label in LABEL_KRITERIA.items():
        bobot_input[kode] = st.number_input(
            label,
            min_value=0.0,
            max_value=1.0,
            value=float(BOBOT_DEFAULT[kode]),
            step=0.01,
            format="%.2f",
            key=f"bobot_{kode}",
        )

    total_bobot = sum(bobot_input.values())
    delta_bobot = total_bobot - 1.0
    if abs(delta_bobot) < 0.001:
        st.success(f"Total bobot: {total_bobot:.2f}")
    else:
        st.error(f"Total bobot: {total_bobot:.2f} (selisih {delta_bobot:+.2f})")

    st.markdown("---")
    st.markdown(
        '<div class="section-label">Template Input</div>', unsafe_allow_html=True
    )
    template_df = buat_template_csv()
    st.download_button(
        label="Unduh Template CSV",
        data=csv_bytes(template_df),
        file_name="template_input_spk.csv",
        mime="text/csv",
        width="stretch",
    )

    st.markdown("---")
    st.caption("PT Cendekia Trust Integrity")
    st.caption("Metode: Simple Additive Weighting (SAW)")
    st.caption(f"Nilai minimum lulus: {NILAI_MIN_LULUS}")


# ─── Header utama ────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="app-header">
    <div>
        <div class="app-title">SPK</div>
        <div class="app-subtitle">Sistem Penunjang Keputusan Seleksi Peserta Pelatihan Kesehatan</div>
        <div class="badge-saw">SAW</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ─── State: proses data ───────────────────────────────────────────────────────

hasil = None

if file_upload is not None:
    try:
        df_raw = pd.read_csv(file_upload)
    except Exception as exc:
        st.error(f"Gagal membaca file CSV: {exc}")
        st.stop()

    if abs(total_bobot - 1.0) > 0.001:
        st.warning(
            "Sesuaikan bobot di sidebar hingga total = 1.0 sebelum menjalankan perhitungan."
        )
    else:
        dengan_spinner = st.spinner("Menghitung SAW...")
        with dengan_spinner:
            hasil = hitung_saw(df_raw, bobot_input)

        if not hasil.sukses:
            st.error(f"Perhitungan gagal: {hasil.pesan_error}")
            hasil = None

else:
    st.info("Upload file CSV di sidebar untuk memulai perhitungan SAW.")


# ─── Konten utama ─────────────────────────────────────────────────────────────

if hasil is not None and hasil.sukses:
    r = hasil.ringkasan
    df = hasil.df_hasil

    # ── Metric row ──
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        st.metric("Total Peserta", r["total_peserta"])
    with col_m2:
        st.metric(
            "Lulus",
            r["total_lulus"],
            delta=f"{r['total_lulus'] / r['total_peserta'] * 100:.1f}%",
        )
    with col_m3:
        st.metric("Tidak Lulus", r["total_tidak_lulus"])
    with col_m4:
        st.metric("Nilai SAW Tertinggi", format_saw(r["nilai_saw_tertinggi"]))
    with col_m5:
        st.metric("Rata-rata SAW", format_saw(r["rata_rata_saw"]))

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    # ── Tabs ──
    tab_rangking, tab_visual, tab_detail, tab_export = st.tabs(
        [
            "Ranking",
            "Visualisasi",
            "Detail Perhitungan",
            "Export",
        ]
    )

    # ════════════════════════════════════════════════
    # TAB 1 - RANKING
    # ════════════════════════════════════════════════
    with tab_rangking:
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 3])
        with col_filter1:
            filter_pelatihan = st.selectbox(
                "Pelatihan",
                options=["Semua"] + r["pelatihan_list"],
                key="filter_pelatihan",
            )
        with col_filter2:
            filter_kelas = st.selectbox(
                "Kelas",
                options=["Semua"] + r["kelas_list"],
                key="filter_kelas",
            )
        with col_filter3:
            filter_status = st.selectbox(
                "Status",
                options=["Semua", "LULUS", "TIDAK LULUS"],
                key="filter_status",
            )

        df_filter = df.copy()
        if filter_pelatihan != "Semua":
            df_filter = df_filter[df_filter["Pelatihan"] == filter_pelatihan]
        if filter_kelas != "Semua":
            df_filter = df_filter[df_filter["Kelas"] == filter_kelas]
        if filter_status != "Semua":
            df_filter = df_filter[df_filter["Status"] == filter_status]

        st.markdown(
            f"<div class='section-label'>Menampilkan {len(df_filter)} dari {len(df)} peserta</div>",
            unsafe_allow_html=True,
        )

        # Kolom tampil di tabel ranking
        kolom_tampil = [
            "No Urut",
            "Peringkat",
            "Nama Peserta",
            "Instansi",
            "Kelas",
            "C1_PreTest",
            "C2_Praktik",
            "C3_PostTest",
            "C4_Keaktifan",
            "C5_Sikap",
            "Nilai SAW",
            "Status",
        ]
        df_show = df_filter[kolom_tampil].copy()
        df_show["Nilai SAW"] = df_show["Nilai SAW"].apply(lambda x: f"{x:.6f}")  # type: ignore[union-attr]

        st.dataframe(
            df_show,
            width="stretch",
            height=480,
            column_config={
                "No Urut": st.column_config.NumberColumn("No", width=50),
                "Peringkat": st.column_config.TextColumn("Rank", width=60),
                "Nama Peserta": st.column_config.TextColumn("Nama Peserta", width=180),
                "Instansi": st.column_config.TextColumn("Instansi", width=200),
                "Kelas": st.column_config.TextColumn("Kelas", width=120),
                "C1_PreTest": st.column_config.NumberColumn(
                    "C1", format="%d", width=60
                ),
                "C2_Praktik": st.column_config.NumberColumn(
                    "C2", format="%d", width=60
                ),
                "C3_PostTest": st.column_config.NumberColumn(
                    "C3", format="%d", width=60
                ),
                "C4_Keaktifan": st.column_config.NumberColumn(
                    "C4", format="%d", width=60
                ),
                "C5_Sikap": st.column_config.NumberColumn("C5", format="%d", width=60),
                "Nilai SAW": st.column_config.TextColumn("Nilai SAW", width=110),
                "Status": st.column_config.TextColumn("Status", width=100),
            },
            hide_index=True,
        )

        # Bar chart ranking
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        fig_ranking = chart_ranking_saw(df_filter)  # type: ignore[arg-type]
        st.plotly_chart(fig_ranking, width="stretch", config={"displayModeBar": False})

    # ════════════════════════════════════════════════
    # TAB 2 - VISUALISASI
    # ════════════════════════════════════════════════
    with tab_visual:
        # Baris 1: Radar
        st.markdown(
            '<div class="section-label">Profil Nilai Kriteria</div>',
            unsafe_allow_html=True,
        )
        fig_radar = chart_radar_kriteria(df)
        st.plotly_chart(fig_radar, width="stretch", config={"displayModeBar": False})

        st.markdown("---")

        # Baris 2: Boxplot
        st.markdown(
            '<div class="section-label">Sebaran Nilai per Kriteria</div>',
            unsafe_allow_html=True,
        )
        fig_box = chart_boxplot_kriteria(df)
        st.plotly_chart(fig_box, width="stretch", config={"displayModeBar": False})

        st.markdown("---")

        # Baris 3: Kontribusi bobot
        st.markdown(
            '<div class="section-label">Kontribusi Bobot Tertimbang (Top 20 Lulus)</div>',
            unsafe_allow_html=True,
        )
        fig_kontribusi = chart_kontribusi_bobot(df)
        st.plotly_chart(
            fig_kontribusi, width="stretch", config={"displayModeBar": False}
        )

        st.markdown("---")

        # Baris 4: Scatter + Instansi
        col_v5, col_v6 = st.columns(2)
        with col_v5:
            st.markdown(
                '<div class="section-label">Perbandingan Dua Kriteria</div>',
                unsafe_allow_html=True,
            )
            opsi_kriteria = {
                "C1 - Pre-Test": ("C1_PreTest", "Pre-Test"),
                "C2 - Praktik": ("C2_Praktik", "Praktik"),
                "C3 - Post-Test": ("C3_PostTest", "Post-Test"),
                "C4 - Keaktifan": ("C4_Keaktifan", "Keaktifan"),
                "C5 - Sikap & Disiplin": ("C5_Sikap", "Sikap & Disiplin"),
            }
            kunci_list = list(opsi_kriteria.keys())
            s_x = st.selectbox("Sumbu X", kunci_list, index=0, key="scatter_x")
            s_y = st.selectbox("Sumbu Y", kunci_list, index=1, key="scatter_y")
            c_x, l_x = opsi_kriteria[s_x]
            c_y, l_y = opsi_kriteria[s_y]
            fig_scatter = chart_scatter_dua_kriteria(df, c_x, c_y, l_x, l_y)
            st.plotly_chart(
                fig_scatter, width="stretch", config={"displayModeBar": False}
            )

        with col_v6:
            st.markdown(
                '<div class="section-label">Peserta Lulus per Instansi</div>',
                unsafe_allow_html=True,
            )
            fig_instansi = chart_instansi(df)
            st.plotly_chart(
                fig_instansi, width="stretch", config={"displayModeBar": False}
            )

    # ════════════════════════════════════════════════
    # TAB 3 - DETAIL PERHITUNGAN
    # ════════════════════════════════════════════════
    with tab_detail:
        st.markdown(
            '<div class="section-label">Bobot yang Digunakan</div>',
            unsafe_allow_html=True,
        )
        df_bobot = pd.DataFrame(
            [
                {
                    "Kode": k.split("_")[0],
                    "Kriteria": LABEL_KRITERIA[k],
                    "Bobot": v,
                    "Bobot (%)": f"{v * 100:.0f}%",
                }
                for k, v in hasil.bobot.items()
            ]
        )
        st.dataframe(df_bobot, width="stretch", hide_index=True, height=220)

        st.markdown("---")
        st.markdown(
            '<div class="section-label">Matriks Normalisasi</div>',
            unsafe_allow_html=True,
        )
        st.caption("Nilai ternormalisasi = Nilai / Nilai Maksimum per kelas")
        st.dataframe(
            hasil.df_normalisasi,
            width="stretch",
            hide_index=True,
            height=350,
        )

        st.markdown("---")
        st.markdown(
            '<div class="section-label">Nilai Terbobot</div>', unsafe_allow_html=True
        )
        st.caption("W*Cx = Nilai Normalisasi × Bobot Kriteria. Nilai SAW = Sigma W*Cx")
        st.dataframe(
            hasil.df_terbobot,
            width="stretch",
            hide_index=True,
            height=350,
        )

        st.markdown("---")

        with st.expander("Penjelasan Metode SAW"):
            st.markdown("""
            **Simple Additive Weighting (SAW)**

            SAW adalah metode MCDM (Multi-Criteria Decision Making) yang menghitung nilai preferensi
            setiap alternatif dengan menjumlahkan hasil perkalian antara rating kinerja yang telah
            dinormalisasi dengan bobot kriteria masing-masing.

            **Langkah Perhitungan:**

            1. **Matriks Keputusan** — Susun nilai asli setiap peserta ke dalam matriks X
            2. **Normalisasi** — Untuk kriteria benefit (semua nilai lebih besar lebih baik):
               - `r_ij = x_ij / max(x_ij)` per kelas
            3. **Nilai Terbobot** — `v_i = Sigma(w_j * r_ij)`
            4. **Ranking** — Urutkan berdasarkan nilai V tertinggi
            5. **Status Kelulusan** — Maks 1 kriteria < 70 dan rata-rata kriteria ≥ 70 harus ≥ 80

            **Kriteria dan Bobot Default:**
            - C1 Pre-Test: 15%
            - C2 Praktik: 35%
            - C3 Post-Test: 20%
            - C4 Keaktifan: 15%
            - C5 Sikap & Disiplin: 15%
            """)

    # ════════════════════════════════════════════════
    # TAB 4 - EXPORT
    # ════════════════════════════════════════════════
    with tab_export:
        st.markdown(
            '<div class="section-label">Download Hasil</div>', unsafe_allow_html=True
        )

        col_e1, col_e2, col_e3 = st.columns(3)

        with col_e1:
            st.download_button(
                label="Hasil Lengkap (CSV)",
                data=csv_bytes(hasil.df_hasil),
                file_name="hasil_saw_acls.csv",
                mime="text/csv",
                width="stretch",
            )
            st.caption("Semua kolom: nilai asli, normalisasi, terbobot, SAW, status")

        with col_e2:
            st.download_button(
                label="Matriks Normalisasi (CSV)",
                data=csv_bytes(hasil.df_normalisasi),
                file_name="normalisasi_matriks.csv",
                mime="text/csv",
                width="stretch",
            )
            st.caption("Nilai N-C1 hingga N-C5")

        with col_e3:
            st.download_button(
                label="Nilai Terbobot (CSV)",
                data=csv_bytes(hasil.df_terbobot),
                file_name="nilai_terbobot_saw.csv",
                mime="text/csv",
                width="stretch",
            )
            st.caption("Nilai W*C1 hingga W*C5 dan Nilai SAW")

        st.markdown("---")

        st.markdown(
            '<div class="section-label">Preview Data</div>', unsafe_allow_html=True
        )

        col_prev1, col_prev2, col_prev3 = st.columns(3)
        if "preview_pilihan" not in st.session_state:
            st.session_state["preview_pilihan"] = "Hasil Lengkap"

        opsi_preview = ["Hasil Lengkap", "Normalisasi", "Terbobot"]
        with col_prev1:
            if st.button(
                "Hasil Lengkap",
                key="btn_prev_lengkap",
                use_container_width=False,
            ):
                st.session_state["preview_pilihan"] = "Hasil Lengkap"
        with col_prev2:
            if st.button(
                "Normalisasi",
                key="btn_prev_norm",
                use_container_width=False,
            ):
                st.session_state["preview_pilihan"] = "Normalisasi"
        with col_prev3:
            if st.button(
                "Terbobot",
                key="btn_prev_terbobot",
                use_container_width=False,
            ):
                st.session_state["preview_pilihan"] = "Terbobot"

        aktif = st.session_state["preview_pilihan"]
        st.markdown(
            f'<div style="font-size:11px; color:#3b82f6; margin:6px 0 10px; font-weight:600;">'
            f"Menampilkan: {aktif}</div>",
            unsafe_allow_html=True,
        )

        peta_preview = {
            "Hasil Lengkap": hasil.df_hasil,
            "Normalisasi": hasil.df_normalisasi,
            "Terbobot": hasil.df_terbobot,
        }
        st.dataframe(peta_preview[aktif], width="stretch", hide_index=True)


# ─── Tampilan awal (belum upload) ─────────────────────────────────────────────

else:
    if file_upload is None:
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            st.markdown(
                """
            <div style="background:#111827; border:1px solid rgba(100,116,139,0.2); border-radius:10px; padding:20px; margin-bottom:12px;">
                <div style="font-size:13px; font-weight:600; color:#93c5fd; margin-bottom:8px;">Cara Penggunaan</div>
                <div style="font-size:12px; color:#94a3b8; line-height:1.7;">
                    1. Unduh template CSV dari sidebar<br>
                    2. Isi data peserta sesuai format<br>
                    3. Upload file CSV melalui sidebar<br>
                    4. Sesuaikan bobot kriteria jika diperlukan<br>
                    5. Hasil perhitungan SAW akan ditampilkan otomatis
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_info2:
            st.markdown(
                """
            <div style="background:#111827; border:1px solid rgba(100,116,139,0.2); border-radius:10px; padding:20px; margin-bottom:12px;">
                <div style="font-size:13px; font-weight:600; color:#93c5fd; margin-bottom:8px;">Kriteria Penilaian (Default)</div>
                <div style="font-size:12px; color:#94a3b8; line-height:1.7;">
                    C1 - Pre-Test &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 15%<br>
                    C2 - Praktik &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 35%<br>
                    C3 - Post-Test &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 20%<br>
                    C4 - Keaktifan &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 15%<br>
                    C5 - Sikap & Disiplin 15%
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
        <div style="background:#111827; border:1px solid rgba(100,116,139,0.2); border-radius:10px; padding:20px;">
            <div style="font-size:13px; font-weight:600; color:#93c5fd; margin-bottom:8px;">Format Kolom CSV</div>
            <div style="font-size:12px; color:#94a3b8; font-family:'DM Mono', monospace; line-height:1.8;">
                No, Nama Peserta, Instansi, Pelatihan, Kelas,<br>
                C1 Pre-Test (15%), C2 Praktik (35%),<br>
                C3 Post-Test (20%), C4 Keaktifan (15%),<br>
                C5 Sikap & Disiplin (15%)
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
