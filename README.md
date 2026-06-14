# MEDISELECT - SPK SAW

Sistem Penunjang Keputusan Seleksi Peserta Pelatihan Kesehatan  
Berbasis Metode Simple Additive Weighting (SAW)  
PT Cendekia Trust Integrity

## Struktur

```
spk_app/
├── app.py              # Entry point Streamlit
├── saw_engine.py       # Engine perhitungan SAW (pure Python)
├── charts.py           # Semua visualisasi Plotly
└── requirements.txt
```

## Jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Input

Upload CSV dengan kolom:

```
No, Nama Peserta, Instansi, Pelatihan, Kelas,
C1 Pre-Test (15%), C2 Praktik (35%),
C3 Post-Test (20%), C4 Keaktifan (15%),
C5 Sikap & Disiplin (15%)
```

Template CSV tersedia via tombol di sidebar.

## Fitur

- Upload CSV, hitung SAW otomatis
- Konfigurasi bobot kriteria live dari sidebar
- Tab Ranking: tabel + filter + bar chart
- Tab Visualisasi: donut, radar, histogram, boxplot, scatter, stacked bar, instansi
- Tab Detail: matriks normalisasi + nilai terbobot + penjelasan metode
- Tab Export: download CSV hasil, normalisasi, terbobot
