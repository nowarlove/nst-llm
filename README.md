# Sistem Pakar Deteksi Kerusakan Hardware iPhone & Chatbot Konsultasi

Sistem pakar diagnosis kerusakan perangkat keras (hardware) iPhone menggunakan kombinasi inferensi **Dempster-Shafer** dan optimasi bobot **Particle Swarm Optimization (PSO)**. Repositori ini juga memuat antarmuka web landing page dan chatbot konsultasi teknis pelanggan untuk workshop **NST Phoneshop** (@nst_ore7).

---

## 1. Ikhtisar Sistem

Sistem ini dirancang untuk mendiagnosis 10 kategori kerusakan perangkat keras iPhone berdasarkan gejala yang diobservasi, menghitung tingkat keyakinan (belief, plausibility, pignistic probability BetP), serta menyajikan estimasi biaya dan tindakan perbaikan:

1. **Layar (LCD / OLED / Touchscreen)**
2. **Baterai**
3. **Port Cas (Charging Port / Flex)**
4. **IC Cas (Tristar / Hydra Charging Controller)**
5. **IC Power (PMIC / Jalur Tegangan VDD)**
6. **Sinyal & Jaringan (Baseband / Transceiver WTR)**
7. **Kamera (Depan / Belakang / Modul OIS)**
8. **Audio (Speaker / Earpiece / Mikrofon / Audio IC)**
9. **Kaca Belakang (Backdoor Housing)**
10. **Pemulihan Perangkat Lunak (iOS / Bootloop)**

---

## 2. Struktur Direktori

```text
deteksiKerusakanIphone/
├── app.py                     # Aplikasi antarmuka dashboard utama (Streamlit)
├── requirements.txt           # Dependensi Python
├── README.md                  # Dokumentasi proyek
├── core/                      # Modul inti komputasi & bisnis
│   ├── clinical_knowledge.py  # Basis pengetahuan gejala dan kerusakan
│   ├── ds_engine.py           # Mesin kombinasi inferensi Dempster-Shafer
│   ├── feature_schema.py      # Validasi skema fitur dan dataset
│   ├── model_manifest.py      # Manajemen manifest & integritas model
│   ├── model_validator.py     # Validasi kontrak model inferensi
│   ├── preprocessing_service.py # Layanan pra-pemrosesan data gejala
│   └── run_experiment.py      # Eksekutor eksperimen & evaluasi
├── data/                      # Dataset & berkas konfigurasi
│   ├── expertDiagnosesAndFix.json # Basis pengetahuan gejala dan estimasi biaya
│   ├── model_schema.json          # Skema formal model inferensi
│   └── experiment_report.json     # Laporan komparasi metrik awal vs PSO
├── models/                    # Notebook eksperimen & pemodelan
│   ├── preprocessing.ipynb    # Alur pra-pemrosesan data
│   └── pso.ipynb              # Implementasi Particle Swarm Optimization
├── chatbot/                   # Antarmuka web & widget chatbot (Dark Mode)
│   ├── index.html             # Landing page bengkel & widget chat
│   ├── style.css              # Sistem desain Dark Mode terstandarisasi
│   ├── script.js              # Logika chatbot terhubung basis pengetahuan
│   ├── .env.example           # Contoh konfigurasi API chatbot
│   └── asset/                 # Foto etalase, stok unit, dan logo resmi NST
├── docs/                      # Dokumentasi komprehensif sistem (MOC)
└── tests/                     # Unit test otomatis
    ├── test_core.py           # Pengujian mesin inferensi DS & model
    ├── test_contracts.py      # Pengujian kontrak runtime vs riset
    └── test_model_manifest.py # Pengujian integritas berkas model
```

---

## 3. Prasyarat & Instalasi

Pastikan telah terpasang **Python 3.10+**.

```bash
# Buat virtual environment (opsional namun disarankan)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Pasang dependensi
pip install -r requirements.txt
```

---

## 4. Cara Menjalankan

### A. Dashboard Antarmuka Sistem Pakar (Streamlit)
Untuk menjalankan aplikasi analisis diagnosis interaktif dan modul evaluasi model:

```bash
streamlit run app.py
```
Aplikasi akan terbuka otomatis pada peramban web di `http://localhost:8501`.

### B. Landing Page & Chatbot Konsultasi NST Phoneshop
Untuk mengakses situs landing page dan chatbot konsultasi pelanggan:
1. Buka berkas `chatbot/index.html` langsung di peramban web atau gunakan local web server:
```bash
python -m http.server 8080 --directory chatbot
```
2. Akses antarmuka pada `http://localhost:8080`.
3. Jika ingin menghubungkan chatbot ke model AI daring, salin `chatbot/.env.example` menjadi `chatbot/.env` dan lengkapi `API_KEY` yang diperlukan. Jika tidak diisi, chatbot otomatis beroperasi menggunakan mesin pengetahuan diagnostik model lokal.

---

## 5. Pengujian Unit Test

Repositori ini dilengkapi rangkaian unit test otomatis untuk menjamin integritas mesin inferensi Dempster-Shafer, kepatuhan skema fitur, dan konsistensi kontrak runtime:

```bash
python -m unittest discover -s tests -v
```

Seluruh 18 kasus uji harus berstatus `OK`.
