"""
charts.py
Semua visualisasi Plotly untuk dashboard MEDISELECT.
Setiap fungsi menerima DataFrame hasil SAW dan mengembalikan go.Figure.
"""

import pandas as pd
import plotly.graph_objects as go

from saw_engine import NILAI_MIN_LULUS

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
    df_top = df.sort_values("Nilai SAW", ascending=False).head(top_n)  # type: ignore[call-overload]

    warna = [WARNA_AKSEN if i == 0 else WARNA_LULUS for i in range(len(df_top))]

    fig = go.Figure(
        go.Bar(
            x=df_top["Nilai SAW"],
            y=df_top["Nama Peserta"],
            orientation="h",
            marker=dict(color=warna, opacity=0.88),
            text=[f"{v:.4f}" for v in df_top["Nilai SAW"]],
            textposition="outside",
            textfont=dict(size=11, color="#94a3b8"),
            hovertemplate=("<b>%{y}</b><br>Nilai SAW: %{x:.6f}<br><extra></extra>"),
        )
    )

    fig.update_yaxes(autorange="reversed", categoryorder="total ascending")
    fig.update_xaxes(range=[0, 1.12])
    _apply_base(fig, "Ranking Peserta Berdasarkan Nilai SAW")
    fig.update_layout(height=max(320, len(df_top) * 28 + 80))
    return fig


# ─── 2. Radar chart rata-rata nilai per kriteria ──────────────────────────────


def chart_radar_kriteria(df: pd.DataFrame) -> go.Figure:
    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    label_cols = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap & Disiplin"]

    def rata(subset):
        return [
            round(subset[c].mean(), 2) if len(subset) > 0 else 0 for c in kriteria_cols
        ]

    r_semua = rata(df)

    cats = label_cols + [label_cols[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=r_semua + [r_semua[0]],
            theta=cats,
            fill="toself",
            fillcolor="rgba(37,99,235,0.18)",
            line=dict(color=WARNA_LULUS, width=2),
            name="Rata-rata",
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
    df_top = df.sort_values("Nilai SAW", ascending=False).head(top_n)  # type: ignore[call-overload]
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
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="markers",
            name="Peserta",
            marker=dict(
                color=WARNA_LULUS,
                size=9,
                opacity=0.8,
                line=dict(width=1, color="#0f172a"),
            ),
            text=df["Nama Peserta"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{x_label}: %{{x}}<br>"
                f"{y_label}: %{{y}}<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=NILAI_MIN_LULUS,
        line_dash="dot",
        line_color="#f59e0b",
        opacity=0.5,
        annotation_text="Min Lulus",
    )
    fig.add_vline(x=NILAI_MIN_LULUS, line_dash="dot", line_color="#f59e0b", opacity=0.5)

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
        y=NILAI_MIN_LULUS,
        line_dash="dash",
        line_color="#f59e0b",
        opacity=0.6,
        annotation_text=f"Batas Lulus ({NILAI_MIN_LULUS})",
    )

    _apply_base(fig, "Distribusi Nilai per Kriteria")
    fig.update_layout(height=360, yaxis_title="Nilai", showlegend=False)
    return fig


# ─── 8. Bar instansi terbanyak ─────────────────────────────────────────


def chart_instansi(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    counts = (
        df.groupby("Instansi")
        .size()
        .reset_index(name="Jumlah")  # type: ignore[call-overload]
        .sort_values("Jumlah", ascending=True)
        .tail(top_n)
    )
    if counts.empty:
        return go.Figure()

    fig = go.Figure(
        go.Bar(
            x=counts["Jumlah"],
            y=counts["Instansi"],
            orientation="h",
            marker=dict(color=WARNA_AKSEN, opacity=0.8),
            hovertemplate="<b>%{y}</b><br>Peserta: %{x}<extra></extra>",
        )
    )

    _apply_base(fig, "Peserta per Instansi")
    fig.update_layout(height=max(280, len(counts) * 26 + 80))
    return fig


# ─── 9. Heatmap nilai normalisasi ─────────────────────────────────────────


def chart_heatmap_normalisasi(df: pd.DataFrame, top_n: int = 30) -> go.Figure:
    """Heatmap nilai N-C1..N-C5 untuk top peserta."""
    df_top = df.sort_values("Nilai SAW", ascending=False).head(top_n)  # type: ignore[call-overload]

    cols_n = ["N-C1", "N-C2", "N-C3", "N-C4", "N-C5"]
    labels = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap"]

    z = df_top[cols_n].values
    y = df_top["Nama Peserta"].tolist()

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=y,
            colorscale="Blues",
            zmin=0,
            zmax=1,
            text=[[f"{v:.3f}" for v in row] for row in z],
            texttemplate="%{text}",
            textfont=dict(size=10, color="#94a3b8"),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.4f}<extra></extra>",
            colorbar=dict(
                title=dict(text="Nilai", font=dict(color="#94a3b8")),
                tickfont=dict(color="#94a3b8"),
            ),
        )
    )

    _apply_base(fig, "Heatmap Nilai Normalisasi")
    fig.update_layout(
        height=max(360, top_n * 24 + 80), yaxis=dict(tickfont=dict(size=10))
    )
    return fig


# ─── 10. Heatmap nilai terbobot ──────────────────────────────────────────


def chart_heatmap_terbobot(df: pd.DataFrame, top_n: int = 30) -> go.Figure:
    """Heatmap nilai W*C1..W*C5 untuk top peserta."""
    df_top = df.sort_values("Nilai SAW", ascending=False).head(top_n)  # type: ignore[call-overload]

    cols_w = ["W*C1", "W*C2", "W*C3", "W*C4", "W*C5"]
    labels = [
        "Pre-Test (15%)",
        "Praktik (35%)",
        "Post-Test (20%)",
        "Keaktifan (15%)",
        "Sikap (15%)",
    ]

    z = df_top[cols_w].values
    y = df_top["Nama Peserta"].tolist()

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=y,
            colorscale="Greens",
            zmin=0,
            zmax=0.35,
            text=[[f"{v:.4f}" for v in row] for row in z],
            texttemplate="%{text}",
            textfont=dict(size=10, color="#94a3b8"),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.4f}<extra></extra>",
            colorbar=dict(
                title=dict(text="Nilai", font=dict(color="#94a3b8")),
                tickfont=dict(color="#94a3b8"),
            ),
        )
    )

    _apply_base(fig, "Heatmap Nilai Terbobot")
    fig.update_layout(
        height=max(360, top_n * 24 + 80), yaxis=dict(tickfont=dict(size=10))
    )
    return fig


# ─── 11. Histogram distribusi Nilai SAW ─────────────────────────────────


def chart_histogram_saw(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df["Nilai SAW"],
            nbinsx=20,
            marker_color=WARNA_LULUS,
            opacity=0.8,
            hovertemplate="Nilai SAW: %{x:.4f}<br>Jumlah: %{y}<extra></extra>",
        )
    )
    _apply_base(fig, "Distribusi Nilai SAW")
    fig.update_layout(height=300, xaxis_title="Nilai SAW", yaxis_title="Jumlah")
    return fig


# ─── 12. Bar bobot kriteria ──────────────────────────────────────────────


def chart_bar_bobot(bobot: dict[str, float]) -> go.Figure:
    label_map = {
        "C1_PreTest": "Pre-Test",
        "C2_Praktik": "Praktik",
        "C3_PostTest": "Post-Test",
        "C4_Keaktifan": "Keaktifan",
        "C5_Sikap": "Sikap",
    }
    labels = [label_map[k] for k in bobot]
    values = [bobot[k] * 100 for k in bobot]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=PALET_KRITERIA, opacity=0.85),
            text=[f"{v:.0f}%" for v in values],
            textposition="outside",
            textfont=dict(size=12, color="#e2e8f0"),
            hovertemplate="<b>%{y}</b>: %{x:.0f}%<extra></extra>",
        )
    )
    _apply_base(fig, "Bobot Kriteria")
    fig.update_layout(height=260, xaxis_title="Bobot (%)", showlegend=False)
    fig.update_xaxes(range=[0, 45])
    return fig


# ─── 13. Korelasi kriteria vs Nilai SAW ─────────────────────────────────


def chart_korelasi_saw(df: pd.DataFrame) -> go.Figure:
    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    labels = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap"]

    corr_vals = [df[c].corr(df["Nilai SAW"]) for c in kriteria_cols]  # type: ignore
    colors = ["#3b82f6" if v > 0 else "#ef4444" for v in corr_vals]

    fig = go.Figure(
        go.Bar(
            x=corr_vals,
            y=labels,
            orientation="h",
            marker=dict(color=colors, opacity=0.85),
            text=[f"{v:.4f}" for v in corr_vals],
            textposition="outside",
            textfont=dict(size=11, color="#94a3b8"),
            hovertemplate="<b>%{y}</b><br>Korelasi dgn SAW: %{x:.4f}<extra></extra>",
        )
    )
    _apply_base(fig, "Korelasi Kriteria vs Nilai SAW")
    fig.update_layout(height=260, xaxis_title="Koefisien Korelasi", showlegend=False)
    fig.add_vline(x=0, line_color="#475569", line_width=1)
    return fig


# ─── 14. Parallel coordinates ────────────────────────────────────────────


def chart_parallel_coords(df: pd.DataFrame, top_n: int = 30) -> go.Figure:
    df_top = df.sort_values("Nilai SAW", ascending=False).head(top_n)  # type: ignore[call-overload]

    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    labels = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap"]

    dimensions = []
    for col, lbl in zip(kriteria_cols, labels):
        dimensions.append(
            dict(
                label=lbl,
                values=df_top[col].tolist(),
                range=[0, 100],
            )
        )
    dimensions.append(
        dict(
            label="Nilai SAW",
            values=df_top["Nilai SAW"].tolist(),
            range=[df_top["Nilai SAW"].min(), df_top["Nilai SAW"].max()],
        )
    )

    fig = go.Figure(
        go.Parcoords(
            line=dict(
                color=df_top["Nilai SAW"],
                colorscale="Blues",
                showscale=True,
                colorbar=dict(
                    title=dict(text="SAW", font=dict(color="#94a3b8", size=10)),
                    tickfont=dict(color="#94a3b8", size=9),
                ),
            ),
            dimensions=dimensions,
        )
    )
    _apply_base(fig, "Parallel Coordinates (Top 30)")
    fig.update_layout(height=380)
    return fig


# ─── 15. Rata-rata SAW per kelas ─────────────────────────────────────────


def chart_rata_saw_per_kelas(df: pd.DataFrame) -> go.Figure:
    rata_per_kelas = df.groupby("Kelas")["Nilai SAW"].mean().sort_values()  # type: ignore[union-attr]
    if rata_per_kelas.empty:
        return go.Figure()

    fig = go.Figure(
        go.Bar(
            x=rata_per_kelas.values,
            y=rata_per_kelas.index.tolist(),
            orientation="h",
            marker=dict(color=WARNA_AKSEN, opacity=0.85),
            text=[f"{v:.4f}" for v in rata_per_kelas.values],
            textposition="outside",
            textfont=dict(size=11, color="#94a3b8"),
            hovertemplate="<b>Kelas %{y}</b><br>Rata-rata SAW: %{x:.4f}<extra></extra>",
        )
    )
    _apply_base(fig, "Rata-rata Nilai SAW per Kelas")
    fig.update_layout(height=max(200, len(rata_per_kelas) * 36 + 60), showlegend=False)
    return fig


# ─── 16. Top 5 vs Bottom 5 ───────────────────────────────────────────────


def chart_top_vs_bottom(df: pd.DataFrame) -> go.Figure:
    df_sorted = df.sort_values("Nilai SAW", ascending=False)
    top5 = df_sorted.head(5)
    bot5 = df_sorted.tail(5)

    kriteria_cols = [
        "C1_PreTest",
        "C2_Praktik",
        "C3_PostTest",
        "C4_Keaktifan",
        "C5_Sikap",
    ]
    labels = ["Pre-Test", "Praktik", "Post-Test", "Keaktifan", "Sikap"]
    cats = labels + [labels[0]]

    r_top = [round(top5[c].mean(), 1) for c in kriteria_cols]
    r_bot = [round(bot5[c].mean(), 1) for c in kriteria_cols]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=r_top + [r_top[0]],
            theta=cats,
            fill="toself",
            fillcolor="rgba(37,99,235,0.2)",
            line=dict(color=WARNA_LULUS, width=2),
            name="Top 5",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=r_bot + [r_bot[0]],
            theta=cats,
            fill="toself",
            fillcolor="rgba(220,38,38,0.15)",
            line=dict(color=WARNA_TIDAK_LULUS, width=2),
            name="Bottom 5",
        )
    )

    fig.update_layout(  # type: ignore[arg-type]
        **LAYOUT_BASE,  # type: ignore[arg-type]
        height=340,
        title=dict(
            text="Top 5 vs Bottom 5",
            font=dict(size=14, color="#94a3b8"),
        ),
        polar=dict(
            bgcolor="#111827",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(100,116,139,0.25)",
                tickfont=dict(size=9, color="#64748b"),
                tickvals=[20, 40, 60, 80, 100],
            ),
            angularaxis=dict(
                gridcolor="rgba(100,116,139,0.25)",
                tickfont=dict(size=10, color="#94a3b8"),
            ),
        ),
    )
    return fig
