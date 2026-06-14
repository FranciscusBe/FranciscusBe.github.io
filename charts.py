"""
charts.py
Semua visualisasi Plotly untuk dashboard MEDISELECT.
Setiap fungsi menerima DataFrame hasil SAW dan mengembalikan go.Figure.
"""

import pandas as pd
import plotly.graph_objects as go

# ─── Palet warna ─────────────────────────────────────────────────────────────

WARNA_LULUS = "#2563eb"
WARNA_TIDAK_LULUS = "#dc2626"
WARNA_AKSEN = "#0ea5e9"
WARNA_NETRAL = "#64748b"
WARNA_GRID = "rgba(100,116,139,0.12)"
FONT_KELUARGA = "DM Sans, Segoe UI, sans-serif"

PALET_KRITERIA = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"]

LAYOUT_BASE = dict(
    font=dict(family=FONT_KELUARGA, size=12, color="#e2e8f0"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        bgcolor="rgba(15,23,42,0.6)",
        bordercolor="rgba(100,116,139,0.3)",
        borderwidth=1,
        font=dict(size=11),
    ),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        **LAYOUT_BASE,  # type: ignore[arg-type]
        title=dict(
            text=title,
            font=dict(size=14, color="#94a3b8"),
            x=0,
            xanchor="left",
            pad=dict(l=0, b=8),
        ),
    )
    fig.update_xaxes(
        gridcolor=WARNA_GRID,
        zerolinecolor=WARNA_GRID,
        tickfont=dict(size=11),
    )
    fig.update_yaxes(
        gridcolor=WARNA_GRID,
        zerolinecolor=WARNA_GRID,
        tickfont=dict(size=11),
    )
    return fig


# ─── 1. Bar chart ranking Nilai SAW ──────────────────────────────────────────


def chart_ranking_saw(df: pd.DataFrame, top_n: int = 25) -> go.Figure:
    df_lulus = (
        df[df["Status"] == "LULUS"]
        .sort_values("Nilai SAW", ascending=False)  # type: ignore[call-overload]
        .head(top_n)
    )

    warna = [WARNA_AKSEN if i == 0 else WARNA_LULUS for i in range(len(df_lulus))]

    fig = go.Figure(
        go.Bar(
            x=df_lulus["Nilai SAW"],
            y=df_lulus["Nama Peserta"],
            orientation="h",
            marker=dict(color=warna, opacity=0.88),
            text=[f"{v:.4f}" for v in df_lulus["Nilai SAW"]],
            textposition="outside",
            textfont=dict(size=11, color="#94a3b8"),
            hovertemplate=("<b>%{y}</b><br>Nilai SAW: %{x:.6f}<br><extra></extra>"),
        )
    )

    fig.update_yaxes(autorange="reversed", categoryorder="total ascending")
    fig.update_xaxes(range=[0, 1.12])
    _apply_base(fig, "Ranking Peserta Berdasarkan Nilai SAW")
    fig.update_layout(height=max(320, len(df_lulus) * 28 + 80))
    return fig


# ─── 2. Donut chart status kelulusan ─────────────────────────────────────────


def chart_donut_status(total_lulus: int, total_tidak_lulus: int) -> go.Figure:
    labels = ["Lulus", "Tidak Lulus"]
    values = [total_lulus, total_tidak_lulus]
    warna = [WARNA_LULUS, WARNA_TIDAK_LULUS]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=warna, line=dict(color="#0f172a", width=2)),
            textfont=dict(size=13),
            hovertemplate="<b>%{label}</b><br>%{value} peserta (%{percent})<extra></extra>",
        )
    )

    total = total_lulus + total_tidak_lulus
    persen_lulus = (total_lulus / total * 100) if total > 0 else 0

    layout = {k: v for k, v in LAYOUT_BASE.items() if k not in ("legend", "margin")}
    fig.update_layout(  # type: ignore[arg-type]
        **layout,  # type: ignore[arg-type]
        height=280,
        annotations=[
            dict(
                text=f"<b>{persen_lulus:.0f}%</b><br><span style='font-size:11px'>Lulus</span>",
                font=dict(size=18, color="#e2e8f0"),
                showarrow=False,
            )
        ],
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
        ),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# ─── 3. Radar chart rata-rata nilai per kriteria ──────────────────────────────


def chart_radar_kriteria(df: pd.DataFrame) -> go.Figure:
    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    label_cols = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap & Disiplin"]

    df_lulus = df[df["Status"] == "LULUS"]
    df_tidak_lulus = df[df["Status"] == "TIDAK LULUS"]

    def rata(subset):
        return [
            round(subset[c].mean(), 2) if len(subset) > 0 else 0 for c in kriteria_cols
        ]

    r_lulus = rata(df_lulus)
    r_tidak_lulus = rata(df_tidak_lulus)
    r_semua = rata(df)

    cats = label_cols + [label_cols[0]]

    fig = go.Figure()

    if len(df_lulus) > 0:
        fig.add_trace(
            go.Scatterpolar(
                r=r_lulus + [r_lulus[0]],
                theta=cats,
                fill="toself",
                fillcolor="rgba(37,99,235,0.18)",
                line=dict(color=WARNA_LULUS, width=2),
                name="Lulus",
            )
        )

    if len(df_tidak_lulus) > 0:
        fig.add_trace(
            go.Scatterpolar(
                r=r_tidak_lulus + [r_tidak_lulus[0]],
                theta=cats,
                fill="toself",
                fillcolor="rgba(220,38,38,0.12)",
                line=dict(color=WARNA_TIDAK_LULUS, width=2),
                name="Tidak Lulus",
            )
        )

    fig.add_trace(
        go.Scatterpolar(
            r=r_semua + [r_semua[0]],
            theta=cats,
            line=dict(color="#f59e0b", width=1.5, dash="dot"),
            name="Rata-rata Semua",
            mode="lines",
        )
    )

    fig.update_layout(  # type: ignore[arg-type]
        **LAYOUT_BASE,  # type: ignore[arg-type]
        height=360,
        polar=dict(
            bgcolor="#111827",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(100,116,139,0.25)",
                linecolor="rgba(100,116,139,0.25)",
                tickfont=dict(size=10, color="#64748b"),
                tickvals=[20, 40, 60, 80, 100],
            ),
            angularaxis=dict(
                gridcolor="rgba(100,116,139,0.25)",
                linecolor="rgba(100,116,139,0.25)",
                tickfont=dict(size=11, color="#94a3b8"),
            ),
        ),
        title=dict(
            text="Profil Rata-rata Nilai per Kriteria",
            font=dict(size=14, color="#94a3b8"),
        ),
    )
    return fig


# ─── 4. Stacked bar kontribusi bobot tertimbang ───────────────────────────────


def chart_kontribusi_bobot(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    df_top = (
        df[df["Status"] == "LULUS"]
        .sort_values("Nilai SAW", ascending=False)  # type: ignore[call-overload]
        .head(top_n)
    )
    if df_top.empty:
        return go.Figure()

    kolom_w = ["W*C1", "W*C2", "W*C3", "W*C4", "W*C5"]
    label_w = [
        "Pre-Test (15%)",
        "Praktik (35%)",
        "Post-Test (20%)",
        "Keaktifan (15%)",
        "Sikap (15%)",
    ]

    fig = go.Figure()
    for i, (col, lbl) in enumerate(zip(kolom_w, label_w)):
        fig.add_trace(
            go.Bar(
                name=lbl,
                x=df_top["Nama Peserta"],
                y=df_top[col],
                marker=dict(color=PALET_KRITERIA[i], opacity=0.85),
                hovertemplate=f"<b>%{{x}}</b><br>{lbl}: %{{y:.4f}}<extra></extra>",
            )
        )

    fig.update_layout(  # type: ignore[arg-type]
        barmode="stack",
        **LAYOUT_BASE,  # type: ignore[arg-type]
        height=380,
        xaxis=dict(tickangle=-35, tickfont=dict(size=10)),
        title=dict(
            text="Kontribusi Bobot Tertimbang per Peserta",
            font=dict(size=14, color="#94a3b8"),
        ),
    )
    return fig


# ─── 5. Scatter plot dua kriteria ────────────────────────────────────────────


def chart_scatter_dua_kriteria(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_label: str,
    y_label: str,
) -> go.Figure:
    warna_map = {"LULUS": WARNA_LULUS, "TIDAK LULUS": WARNA_TIDAK_LULUS}

    fig = go.Figure()
    for status, grp in df.groupby("Status"):
        fig.add_trace(
            go.Scatter(
                x=grp[x_col],
                y=grp[y_col],
                mode="markers",
                name=status,
                marker=dict(
                    color=warna_map.get(str(status), WARNA_NETRAL),
                    size=9,
                    opacity=0.8,
                    line=dict(width=1, color="#0f172a"),
                ),
                text=grp["Nama Peserta"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{x_label}: %{{x}}<br>"
                    f"{y_label}: %{{y}}<extra></extra>"
                ),
            )
        )

    fig.add_hline(
        y=60,
        line_dash="dot",
        line_color="#f59e0b",
        opacity=0.5,
        annotation_text="Min Lulus",
    )
    fig.add_vline(x=60, line_dash="dot", line_color="#f59e0b", opacity=0.5)

    _apply_base(fig, f"{x_label} vs {y_label}")
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)
    fig.update_layout(height=380)
    return fig


# ─── 6. Box plot nilai per kriteria ──────────────────────────────────────────


def chart_boxplot_kriteria(df: pd.DataFrame) -> go.Figure:
    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    label_cols = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap & Disiplin"]

    fig = go.Figure()
    for i, (col, lbl) in enumerate(zip(kriteria_cols, label_cols)):
        fig.add_trace(
            go.Box(
                y=df[col],
                name=lbl,
                marker_color=PALET_KRITERIA[i],
                line_color=PALET_KRITERIA[i],
                fillcolor=f"rgba({int(PALET_KRITERIA[i][1:3], 16)},{int(PALET_KRITERIA[i][3:5], 16)},{int(PALET_KRITERIA[i][5:7], 16)},0.15)",
                boxmean=True,
                hovertemplate=f"<b>{lbl}</b><br>%{{y}}<extra></extra>",
            )
        )

    fig.add_hline(
        y=60,
        line_dash="dash",
        line_color="#f59e0b",
        opacity=0.6,
        annotation_text="Batas Lulus (60)",
    )

    _apply_base(fig, "Distribusi Nilai per Kriteria")
    fig.update_layout(height=360, yaxis_title="Nilai", showlegend=False)
    return fig


# ─── 8. Bar instansi terbanyak lulus ─────────────────────────────────────────


def chart_instansi(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    df_lulus = df[df["Status"] == "LULUS"]
    if df_lulus.empty:
        return go.Figure()

    counts = (
        df_lulus.groupby("Instansi")
        .size()
        .reset_index(name="Jumlah")  # type: ignore[call-overload]
        .sort_values("Jumlah", ascending=True)
        .tail(top_n)
    )

    fig = go.Figure(
        go.Bar(
            x=counts["Jumlah"],
            y=counts["Instansi"],
            orientation="h",
            marker=dict(color=WARNA_AKSEN, opacity=0.8),
            hovertemplate="<b>%{y}</b><br>Lulus: %{x}<extra></extra>",
        )
    )

    _apply_base(fig, "Peserta Lulus per Instansi")
    fig.update_layout(height=max(280, len(counts) * 26 + 80))
    return fig
