import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.preprocessing_service import (
    SLANG_MAP,
    execute_full_preprocessing,
    normalize_text,
)
from core.run_experiment import (
    ExperimentEngine,
    constrain,
    file_hash,
    metrics,
    optimize,
)

# -----------------------------------------------------------------------------
# Inisialisasi Otomatis Dataset jika Berkas Belum Tersedia di Disk
# -----------------------------------------------------------------------------
train_dir = ROOT_DIR / "data" / "dataLatih"
test_dir = ROOT_DIR / "data" / "dataUji"
target_train_csv = train_dir / "dataLatih-2026-08-29-20-08.csv"
target_test_csv = test_dir / "dataUji-2026-08-29-20-08.csv"

if not target_train_csv.is_file() or not target_test_csv.is_file():
    try:
        execute_full_preprocessing()
    except Exception:
        pass

# -----------------------------------------------------------------------------
# Konfigurasi Halaman dan Desain
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Model Execution Hub - Deteksi Kerusakan iPhone",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #E2E8F0 !important;
        margin-bottom: 1.2rem;
    }
    .sub-title code {
        color: #38BDF8 !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 8px 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Navigasi Sidebar
# -----------------------------------------------------------------------------
st.sidebar.title("Pipeline Model")
st.sidebar.caption("Folder models/ Deteksi Kerusakan iPhone")

selected_model = st.sidebar.radio(
    "Pilih Tahapan Model:",
    [
        "1. models/preprocessing.ipynb (Data Pipeline & Fitur)",
        "2. models/pso.ipynb (DS Awal & Optimasi DS-PSO)",
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.markdown(
    """
    **Urutan Eksekusi Penelitian:**
    1. **Tahap 1:** `preprocessing.ipynb`  
       Mengolah data mentah Excel teknisi menjadi dataset latih (736) dan uji (185).
    2. **Tahap 2:** `pso.ipynb`  
       Melatih model Dempster-Shafer dan mengoptimasi bobot belief dengan PSO.
    """
)

# =============================================================================
# MODUL 1: models/preprocessing.ipynb
# =============================================================================
if selected_model == "1. models/preprocessing.ipynb (Data Pipeline & Fitur)":
    st.markdown('<div class="main-title">Tahap 1: Pipeline Preprocessing dan Ekstraksi Fitur</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Menjalankan alur <code>models/preprocessing.ipynb</code>: Membaca data mentah Excel, '
        'membersihkan istilah non-baku teknisi, memfilter hardware iPhone, mengekstrak 14 fitur terstruktur, '
        'dan membagi dataset menjadi data latih (80%) dan data uji (20%).</div>',
        unsafe_allow_html=True,
    )

    toko_path = ROOT_DIR / "data" / "data toko 2.xlsx"
    utama_path = ROOT_DIR / "data" / "data utama.xlsx"

    is_dataset_ready = target_train_csv.is_file() and target_test_csv.is_file()
    if is_dataset_ready:
        st.success("Status Dataset: Berkas data latih (736 kasus) dan data uji (185 kasus) sudah tersedia di folder data/.")
    else:
        st.warning("Status Dataset: Berkas data latih dan data uji belum diekspor. Silakan gunakan tab '4. Eksekusi Pipeline & Ekspor Dataset' di bawah.")

    tab_load, tab_slang, tab_filter, tab_exec = st.tabs([
        "1. Loading Data Awal",
        "2. Kamus Slang & Normalizer Teks",
        "3. Filter Hardware & Anti-Leakage",
        "4. Eksekusi Pipeline & Ekspor Dataset",
    ])

    # TAB 1: LOADING DATA AWAL
    with tab_load:
        st.subheader("1. Loading Data Awal dari Excel")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode untuk Loading Data Awal (NST Phoneshop & Toko Rekan):**\n\n"
                "Potongan kode berikut merupakan fungsi inti pembacaan data mentah Excel "
                "sebagaimana diterapkan pada `models/preprocessing.ipynb` (Tahap 1) dan `core/preprocessing_service.py`:"
            )
            st.code(
                """import os
import pandas as pd

data_dir = "data"
utama_path = os.path.join(data_dir, "data utama.xlsx")
toko_path = os.path.join(data_dir, "data toko 2.xlsx")

# 1. Loading data utama bengkel NST Phoneshop (500 baris, 7 kolom)
# header=None digunakan agar baris awal pencatatan teknisi NST tidak terpotong sebagai nama kolom
df_utama = pd.read_excel(utama_path, header=None)

# 2. Loading data pendukung toko rekan (Sheet JAN dan FEB digabung menjadi 616 baris, 10 kolom)
df_jan = pd.read_excel(toko_path, sheet_name="JAN")
df_feb = pd.read_excel(toko_path, sheet_name="FEB")
df_toko = pd.concat([df_jan, df_feb], ignore_index=True)""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/preprocessing.ipynb (Cell 2) dan core/preprocessing_service.py (execute_full_preprocessing)."
            )

        if toko_path.is_file() and utama_path.is_file():
            df_jan = pd.read_excel(toko_path, sheet_name="JAN")
            df_feb = pd.read_excel(toko_path, sheet_name="FEB")
            df_toko = pd.concat([df_jan, df_feb], ignore_index=True)
            df_utama = pd.read_excel(utama_path, header=None)

            c1, c2, c3 = st.columns(3)
            c1.metric("NST Phoneshop (Data Utama)", f"{len(df_utama)} baris", f"{df_utama.shape[1]} kolom")
            c2.metric("Toko Rekan (Data Toko 2)", f"{len(df_toko)} baris", f"{df_toko.shape[1]} kolom")
            c3.metric("Total Baris Mentah", f"{len(df_utama) + len(df_toko):,} baris")

            st.write("**Jumlah Baris Awal per Sumber:**")
            df_ringkasan_sumber = pd.DataFrame({
                "Sumber": ["NST Phoneshop", "Toko rekan"],
                "Baris awal": [len(df_utama), len(df_toko)],
            })
            st.dataframe(df_ringkasan_sumber, width="stretch")

            with st.expander("Cuplikan 5 Baris Data Toko Rekan (Sheet JAN dan FEB)"):
                st.dataframe(df_toko.head().astype(str), width="stretch")

            with st.expander("Cuplikan 5 Baris Data Utama NST"):
                st.dataframe(df_utama.head().astype(str), width="stretch")
        else:
            st.error("File excel dataset mentah tidak ditemukan di folder data/.")

    # TAB 2: KAMUS SLANG
    with tab_slang:
        st.subheader("2. Normalisasi Teks (Lexicon Normalization) dan Kamus Slang")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Normalisasi Teks dan Slang:**\n\n"
                "Fungsi berikut memetakan istilah slang dan singkatan non-baku teknisi menggunakan regex `\\b` "
                "ke kosakata baku bahasa Indonesia sebelum ekstraksi fitur dilakukan:"
            )
            st.code(
                """import re

# Kamus regex pemetaan istilah non-baku teknisi ke kata baku bahasa Indonesia
SLANG_MAP = {
    r'\\bbatrai\\b': 'baterai',
    r'\\bbatre\\b': 'baterai',
    r'\\bgembung\\b': 'kembung',
    r'\\bgakbisa\\b': 'tidak bisa',
    r'\\bkoncas\\b': 'konektor cas',
    r'\\bmatot\\b': 'mati total',
    r'\\bshort\\b': 'korsleting',
    r'\\bts\\b': 'touchscreen',
    r'\\bbackdor\\b': 'backdoor',
    r'\\bonoff\\b': 'on/off',
    # ... total 43 pola regex teknisi
}

def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text)
    return re.sub(r'\\s+', ' ', text).strip()""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/preprocessing.ipynb (Cell 4) dan core/preprocessing_service.py (normalize_text)."
            )

        st.markdown(
            "Mengubah istilah non-baku, singkatan teknisi, dan salah ketik (typo) ke bentuk baku bahasa Indonesia "
            "sebelum ekstraksi fitur dilakukan."
        )

        st.write("**Uji Coba Normalisasi Slang Interaktif:**")
        user_input_slang = st.text_input(
            "Ketik kalimat keluhan teknisi non-baku:",
            value="hp matot pas dicharge, batre gembung bckdor pecah, tombol onoff gak bisa",
        )
        hasil_normalisasi = normalize_text(user_input_slang)

        col_in, col_out = st.columns(2)
        col_in.info(f"Teks Asli Teknisi:\n\n{user_input_slang}")
        col_out.success(f"Hasil Normalisasi Baku:\n\n{hasil_normalisasi}")

        with st.expander(f"Daftar Kamus Pemetaan Slang ({len(SLANG_MAP)} Pola Regex)"):
            df_slang = pd.DataFrame([
                {"Pola Regex Istilah Non-Baku": pat, "Kata Baku Pengganti": rep}
                for pat, rep in SLANG_MAP.items()
            ])
            st.dataframe(df_slang, width="stretch")

    # TAB 3: FILTER HARDWARE
    with tab_filter:
        st.subheader("3. Filter Kasus Hardware dan Penanganan Target Leakage")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Filter Hardware dan Pencegahan Target Leakage:**\n\n"
                "Kode ini memisahkan kasus perbaikan fisik hardware dari kasus software/iCloud, serta "
                "menghapus kata kerja tindakan servis teknisi agar model objektif mendiagnosis berdasarkan gejala murni:"
            )
            st.code(
                """# 1. Filter Kasus Non-Hardware (Penyaringan kasus Software, iCloud, Pola)
sw_keywords = [
    'lupa pola', 'flash', 'sofware', 'software', 'instal ulang', 
    'icloud', 'cleaning', 'stuck logo', 'bypass', 'downgrade'
]
is_hardware = not any(k in symptom_text for k in sw_keywords) and ('IPHONE' in tipe_hp)

# 2. Pencegahan Target Leakage (Menghilangkan kata kerja aksi servis)
action_verbs = ['ganti ', 'servis ', 'lem ulang ', 'lem ', 'bersihkan ', 'cek ']
symptom_cleaned = text_keluhan
for verb in action_verbs:
    symptom_cleaned = symptom_cleaned.replace(verb, '')""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/preprocessing.ipynb (Cell 6 & 7) dan core/preprocessing_service.py (execute_full_preprocessing)."
            )

        st.markdown(
            "1. **Penyaringan Software**: Kasus non-hardware dibuang (lupa pola, flash, software, instal ulang, icloud, cleaning, stuck logo, bypass, downgrade).\n"
            "2. **Pencegahan Target Leakage**: Kata kerja aksi servis pada Toko 2 (ganti, servis, lem ulang, lem, bersihkan, cek) dihilangkan dari teks gejala agar model tidak bergantung pada tindakan teknisi."
        )

        st.info("Hasil Filter: Dari total 1.116 baris awal, sebanyak 1.012 baris lolos verifikasi sebagai kasus hardware iPhone, dan 921 baris terpetakan lengkap ke 14 fitur gejala.")

    # TAB 4: EKSEKUSI PIPELINE
    with tab_exec:
        st.subheader("4. Eksekusi Pipeline Preprocessing dan Ekspor Dataset (80:20)")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Ekstraksi Fitur dan Pembagian Dataset (80:20):**\n\n"
                "Kode ini mengekstrak 14 fitur gejala menggunakan aturan pemetaan teknis pakar, "
                "kemudian membagi dataset secara terstratifikasi menjadi 80% data latih dan 20% data uji:"
            )
            st.code(
                """from sklearn.model_selection import train_test_split

# 1. Ekstraksi 14 Fitur Gejala (Signal, Baterai, LCD, Wifi, Touchscreen, Tegangan, dll.)
df_mapped = pd.DataFrame([map_row(row, wifi_reviews) for _, row in df_raw.iterrows()])

# 2. Stratified Train/Test Split (80% Data Latih : 20% Data Uji)
# Kelas langka (jumlah <= 2) dialokasikan otomatis ke data latih untuk mencegah unrepresented class di uji
df_train, df_test = train_test_split(
    df_normal, 
    test_size=0.20, 
    stratify=df_normal['Kerusakan'], 
    random_state=42
)
df_train = pd.concat([df_train, df_rare], ignore_index=True)""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/preprocessing.ipynb (Cell 9-12) dan core/preprocessing_service.py."
            )

        st.markdown(
            "Tombol di bawah ini akan menjalankan seluruh tahapan models/preprocessing.ipynb secara otomatis:\n"
            "- Membaca berkas Excel mentah.\n"
            "- Menerapkan normalisasi slang dan filter hardware.\n"
            "- Mengekstrak 14 fitur gejala terstruktur.\n"
            "- Melakukan Stratified Train/Test Split (80% Data Latih, 20% Data Uji).\n"
            "- Menyimpan hasilnya ke folder data/dataLatih/ dan data/dataUji/."
        )

        if st.button("Jalankan Pipeline Preprocessing Sekarang", type="primary"):
            with st.spinner("Menjalankan pipeline preprocessing data..."):
                try:
                    res = execute_full_preprocessing()
                    st.success("Pipeline Preprocessing Selesai.")

                    r1, r2, r3 = st.columns(3)
                    r1.metric("Data Lolos Filter", f"{res['hardware_lolos']} kasus", "Hardware Only")
                    r2.metric("Data Latih (80%)", f"{res['train_count']} kasus", "data/dataLatih")
                    r3.metric("Data Uji (20%)", f"{res['test_count']} kasus", "data/dataUji")

                    st.write("**Distribusi Kelas Kerusakan (Data Latih vs Uji):**")
                    cnt_train = res['df_train']['Kerusakan'].value_counts().rename("Latih (80%)")
                    cnt_test = res['df_test']['Kerusakan'].value_counts().rename("Uji (20%)")
                    df_dist = pd.concat([cnt_train, cnt_test], axis=1).fillna(0).astype(int)
                    df_dist["Total"] = df_dist["Latih (80%)"] + df_dist["Uji (20%)"]
                    st.dataframe(df_dist, width="stretch")

                    st.info("Dataset telah selesai diekspor. Anda dapat membuka menu 2. models/pso.ipynb untuk melihat pelatihan model.")
                except Exception as e:
                    st.error(f"Gagal menjalankan preprocessing: {e}")

        if target_train_csv.is_file():
            df_cur_train = pd.read_csv(target_train_csv)
            with st.expander(f"Cuplikan 10 Baris Data Latih ({len(df_cur_train)} baris)"):
                st.dataframe(df_cur_train.head(10).astype(str), width="stretch")


# =============================================================================
# MODUL 2: models/pso.ipynb
# =============================================================================
elif selected_model == "2. models/pso.ipynb (DS Awal & Optimasi DS-PSO)":
    st.markdown('<div class="main-title">Tahap 2: Evaluasi DS Awal dan Optimasi PSO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Menjalankan alur <code>models/pso.ipynb</code>: Evaluasi baseline Dempster-Shafer awal '
        'pada 185 data uji, optimasi Particle Swarm Optimization (10 Seed: 42-51) pada 736 data latih, '
        'serta komparasi metrik penelitian.</div>',
        unsafe_allow_html=True,
    )

    report_path = ROOT_DIR / "data" / "experiment_report.json"
    belief_path = ROOT_DIR / "data" / "belief.json"

    if not report_path.is_file() or not belief_path.is_file():
        st.error("File laporan data/experiment_report.json atau data/belief.json tidak ditemukan.")
        st.stop()

    arsip = json.loads(report_path.read_text(encoding="utf-8"))
    metadata = arsip["metadata"]
    train_path = ROOT_DIR / metadata["train"]
    test_path = ROOT_DIR / metadata["test"]

    has_live_dataset = train_path.is_file() and test_path.is_file()
    if not has_live_dataset:
        st.warning(
            "Berkas Data Latih atau Data Uji belum ditemukan di disk.\n\n"
            "Anda dapat membuat dataset tersebut secara instan dengan tombol di bawah ini."
        )
        if st.button("Ekspor Dataset Sekarang (Auto Preprocessing)", type="primary"):
            with st.spinner("Mengekspor dataset dari data mentah..."):
                try:
                    execute_full_preprocessing()
                    st.success("Dataset berhasil dibuat. Halaman akan diperbarui.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal mengekspor dataset: {e}")
                    st.stop()

    if has_live_dataset:
        df_train = pd.read_csv(train_path)
        df_test = pd.read_csv(test_path)
        rules_raw = json.loads(belief_path.read_text(encoding="utf-8"))["rules"]
        initial_params = [hyp["initial_belief"] for r in rules_raw for hyp in r["hypotheses"]]
        classes = sorted(df_train["Kerusakan"].unique().tolist())
        counts = df_train["Kerusakan"].value_counts()
        priors = {name: float(counts.get(name, 0) / len(df_train)) for name in classes}
        engine = ExperimentEngine(rules_raw, classes, priors)
        train_active = engine.active_rules(df_train)
        test_active = engine.active_rules(df_test)
        initial_belief = constrain(initial_params, rules_raw)
        y_test = df_test["Kerusakan"].to_numpy()

    tab_ds, tab_pso, tab_compare, tab_vis, tab_runner = st.tabs([
        "1. DS Awal (Baseline)",
        "2. Hasil 10 Run PSO (Seed 42-51)",
        "3. Rangkuman & Komparasi Metrik",
        "4. Visualisasi (Konvergensi & CM)",
        "5. Jalankan PSO Swarm",
    ])

    # TAB 1: DS AWAL
    with tab_ds:
        st.subheader("1. Evaluasi DS Awal pada Data Uji")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Inferensi Dempster-Shafer (Kombinasi Bukti & Pignistik BetP):**\n\n"
                "Fungsi berikut menggabungkan massa keyakinan dari aturan gejala aktif dan menghitung "
                "probabilitas pignistik untuk menentukan kelas kerusakan dengan probabilitas tertinggi:"
            )
            st.code(
                """# 1. Aturan Kombinasi Dempster-Shafer (Dempster's Rule of Combination)
def combine(first_mass, second_mass, theta):
    combined, conflict = {}, 0.0
    for left, left_m in first_mass.items():
        for right, right_m in second_mass.items():
            intersection = left.intersection(right)
            if intersection:
                combined[intersection] = combined.get(intersection, 0.0) + left_m * right_m
            else:
                conflict += left_m * right_m
    # Orthogonal sum ternormalisasi terhadap faktor konflik (1 - K)
    return {k: mass / (1.0 - conflict) for k, mass in combined.items()}

# 2. Transformasi Probabilitas Pignistik (BetP) membagi massa Theta secara adil
def pignistic_probabilities(combined_mass, classes, theta):
    theta_share = combined_mass.get(theta, 0.0) / len(classes)
    probs = {c: sum(m / len(s) for s, m in combined_mass.items() if c in s) + theta_share for c in classes}
    return probs""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/pso.ipynb (Cell 3 & 4) dan core/run_experiment.py (ExperimentEngine)."
            )

        st.markdown(
            "Aturan aktif digabungkan dengan belief awal pakar dari data/belief.json, "
            "kemudian ketidakpastian massa Theta dibagi ke seluruh kelas (probabilitas pignistik)."
        )

        base_metrics = arsip["baseline_ds"]
        base_acc = base_metrics["accuracy"]
        base_macro = base_metrics["macro_f1"]
        base_weighted = base_metrics["weighted_f1"]
        base_brier = base_metrics["multiclass_brier"]
        total_uji = base_metrics["confusion_matrix"]
        total_kasus_uji = sum(sum(r) for r in total_uji)
        benar_ds = round(base_acc * total_kasus_uji)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Akurasi DS Awal", f"{base_acc:.2%}", f"{benar_ds}/{total_kasus_uji} kasus benar")
        m2.metric("Macro F1", f"{base_macro:.2%}")
        m3.metric("Weighted F1", f"{base_weighted:.2%}")
        m4.metric("Brier Score", f"{base_brier:.4f}")

        st.write("**Tabel Metrik DS Awal:**")
        df_baseline_table = pd.DataFrame({
            "Metrik": ["Accuracy", "Macro F1", "Weighted F1", "Brier score"],
            "DS awal": [
                f"{base_acc:.2%}".replace(".", ","),
                f"{base_macro:.2%}".replace(".", ","),
                f"{base_weighted:.2%}".replace(".", ","),
                f"{base_brier:.4f}".replace(".", ","),
            ],
        })
        st.dataframe(df_baseline_table, width="stretch")

        with st.expander("Detail Classification Report Per-Kelas (DS Awal)"):
            st.dataframe(pd.DataFrame(base_metrics["classification_report"]).T, width="stretch")

    # TAB 2: OPTIMASI PSO
    with tab_pso:
        st.subheader("2. Hasil Optimasi PSO pada Data Latih (10 Seed: 42-51)")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Optimasi Particle Swarm Optimization (PSO):**\n\n"
                "Algoritma PSO mengoptimasi bobot belief partikel berdasarkan fungsi fitness (1 - Multiclass Brier Score) "
                "dengan memperbarui kecepatan dan posisi partikel setiap iterasi:"
            )
            st.code(
                """# 1. Fungsi Fitness Partikel (1 - Multiclass Brier Score pada Data Latih)
def fitness(position, active_train, target_one_hot):
    probs = engine.matrix(active_train, position)
    return 1.0 - float(np.mean(np.sum((probs - target_one_hot) ** 2, axis=1)))

# 2. Pembaruan Kecepatan & Posisi Partikel PSO
# v_id(t+1) = w * v_id(t) + c1 * r1 * (pbest - x_id) + c2 * r2 * (gbest - x_id)
# x_id(t+1) = constrain(x_id(t) + v_id(t+1))
velocity = inertia * velocity + 2.0 * r1 * (pbest - pos) + 2.0 * r2 * (gbest - pos)
position = constrain(position + velocity, rules)""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/pso.ipynb (Cell 6 & 7) dan core/run_experiment.py (optimize)."
            )

        st.markdown(
            "Fitness tiap partikel dihitung hanya pada data latih sebagai 1 - Multiclass Brier. "
            "Setiap seed menjalankan 30 partikel dan 100 iterasi. "
            "Setelah itu, belief optimal dievaluasi pada data uji (185 kasus)."
        )

        runs_data = arsip["runs"]
        df_pso_runs = pd.DataFrame([
            {
                "Seed": run["seed"],
                "Fitness Latih": f"{run['train_fitness']:.6f}",
                "Accuracy Uji": f"{run['metrics']['accuracy']:.2%}",
                "Macro F1 Uji": f"{run['metrics']['macro_f1']:.2%}",
                "Weighted F1 Uji": f"{run['metrics']['weighted_f1']:.2%}",
                "Brier Score Uji": f"{run['metrics']['multiclass_brier']:.4f}",
            }
            for run in runs_data
        ])
        st.dataframe(df_pso_runs, width="stretch")

    # TAB 3: RANGKUMAN & PERBANDINGAN
    with tab_compare:
        st.subheader("3. Perbandingan DS Awal vs DS-PSO")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Evaluasi Komparatif Metrik:**\n\n"
                "Fungsi berikut menghitung metrik evaluasi komparatif (Akurasi, Macro F1, Weighted F1, dan Brier Score) "
                "antara model baseline DS awal dan model teroptimasi PSO pada 185 data uji:"
            )
            st.code(
                """from sklearn.metrics import accuracy_score, classification_report

# 1. Evaluasi Akurasi dan F1-Score
acc = accuracy_score(y_true, y_pred)
report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
macro_f1 = report["macro avg"]["f1-score"]
weighted_f1 = report["weighted avg"]["f1-score"]

# 2. Multiclass Brier Score (Probabilistic Calibration)
brier_score = float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/pso.ipynb (Cell 8 & 9) dan core/run_experiment.py (metrics)."
            )

        acc_list = [r["metrics"]["accuracy"] for r in runs_data]
        macro_list = [r["metrics"]["macro_f1"] for r in runs_data]
        weighted_list = [r["metrics"]["weighted_f1"] for r in runs_data]
        brier_list = [r["metrics"]["multiclass_brier"] for r in runs_data]

        best_run = arsip["best_run"]

        col_sum1, col_sum2 = st.columns(2)
        with col_sum1:
            st.write("**Statistik DS-PSO (Rata-rata dan Standar Deviasi):**")
            df_stats = pd.DataFrame({
                "Statistik": ["mean", "std"],
                "Accuracy": [f"{np.mean(acc_list):.6f}", f"{np.std(acc_list, ddof=1):.6f}"],
                "Macro F1": [f"{np.mean(macro_list):.6f}", f"{np.std(macro_list, ddof=1):.6f}"],
                "Weighted F1": [f"{np.mean(weighted_list):.6f}", f"{np.std(weighted_list, ddof=1):.6f}"],
                "Brier score": [f"{np.mean(brier_list):.6f}", f"{np.std(brier_list, ddof=1):.6f}"],
            })
            st.dataframe(df_stats, width="stretch")

        with col_sum2:
            st.info(
                f"**Seed Terbaik: Seed {best_run['seed']}**\n\n"
                f"- Prediksi Benar: {round(best_run['metrics']['accuracy'] * total_kasus_uji)}/{total_kasus_uji} kasus\n"
                f"- Akurasi: {best_run['metrics']['accuracy']:.2%}\n"
                f"- Macro F1: {best_run['metrics']['macro_f1']:.2%}\n"
                f"- Brier Score: {best_run['metrics']['multiclass_brier']:.4f}\n"
                f"- Peningkatan Akurasi: +{(best_run['metrics']['accuracy'] - base_acc) * 100:.2f} poin persentase"
            )

        st.write("**Tabel Perbandingan Lengkap:**")
        df_comp = pd.DataFrame([
            {
                "Metrik": "Accuracy",
                "DS awal": f"{base_acc:.2%}",
                "DS PSO rata-rata": f"{np.mean(acc_list):.2%}",
                "DS PSO terbaik": f"{best_run['metrics']['accuracy']:.2%}",
                "Perubahan terbaik dari DS": f"+{(best_run['metrics']['accuracy'] - base_acc) * 100:.2f} poin persentase",
            },
            {
                "Metrik": "Macro F1",
                "DS awal": f"{base_macro:.2%}",
                "DS PSO rata-rata": f"{np.mean(macro_list):.2%}",
                "DS PSO terbaik": f"{best_run['metrics']['macro_f1']:.2%}",
                "Perubahan terbaik dari DS": f"+{(best_run['metrics']['macro_f1'] - base_macro) * 100:.2f} poin persentase",
            },
            {
                "Metrik": "Weighted F1",
                "DS awal": f"{base_weighted:.2%}",
                "DS PSO rata-rata": f"{np.mean(weighted_list):.2%}",
                "DS PSO terbaik": f"{best_run['metrics']['weighted_f1']:.2%}",
                "Perubahan terbaik dari DS": f"+{(best_run['metrics']['weighted_f1'] - base_weighted) * 100:.2f} poin persentase",
            },
            {
                "Metrik": "Brier score",
                "DS awal": f"{base_brier:.4f}",
                "DS PSO rata-rata": f"{np.mean(brier_list):.4f}",
                "DS PSO terbaik": f"{best_run['metrics']['multiclass_brier']:.4f}",
                "Perubahan terbaik dari DS": f"{base_brier - best_run['metrics']['multiclass_brier']:.4f} (turun)",
            },
        ])
        st.dataframe(df_comp, width="stretch")

    # TAB 4: VISUALISASI
    with tab_vis:
        st.subheader("4. Visualisasi Kurva Konvergensi dan Confusion Matrix")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode Visualisasi Evaluasi Model:**\n\n"
                "Kode berikut menghasilkan grafik kurva konvergensi fitness PSO per iterasi dan "
                "heatmap Confusion Matrix untuk mendeteksi sebaran prediksi per kelas:"
            )
            st.code(
                """import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# 1. Plotting Kurva Konvergensi PSO Fitness per Iterasi
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(history, label=f"Seed {best_seed}", color="#0284C7", lw=2)
ax.set_xlabel("Iterasi")
ax.set_ylabel("Fitness (1 - Brier Latih)")

# 2. Heatmap Confusion Matrix Data Uji
cm = confusion_matrix(y_true, y_pred, labels=classes)
cax = ax.matshow(cm, cmap="Blues")""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/pso.ipynb (Cell 10 & 11) dan core/run_experiment.py."
            )

        vis_col1, vis_col2 = st.columns(2)

        with vis_col1:
            st.write("**Kurva Konvergensi PSO (Seed Terbaik: " + str(best_run['seed']) + "):**")
            fig, ax = plt.subplots(figsize=(7, 4.5))
            history = best_run.get("history", [])
            if history:
                ax.plot(history, label=f"Seed {best_run['seed']}", color="#0284C7", lw=2)
            ax.set_xlabel("Iterasi")
            ax.set_ylabel("Fitness (1 - Brier Latih)")
            ax.set_title(f"Konvergensi PSO Seed {best_run['seed']}")
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

        with vis_col2:
            st.write(f"**Confusion Matrix Data Uji (Seed Terbaik: {best_run['seed']}):**")
            cm = np.array(best_run["metrics"]["confusion_matrix"])
            cls_names = list(base_metrics["classification_report"].keys())[:-3]
            fig, ax = plt.subplots(figsize=(7, 6))
            cax = ax.matshow(cm, cmap="Blues", alpha=0.85)
            fig.colorbar(cax)

            for i in range(len(cls_names)):
                for j in range(len(cls_names)):
                    val = cm[i, j]
                    if val > 0:
                        ax.text(j, i, str(val), ha="center", va="center", color="black" if val < cm.max() / 2 else "white", fontsize=8)

            ax.set_xticks(range(len(cls_names)))
            ax.set_yticks(range(len(cls_names)))
            ax.set_xticklabels(cls_names, rotation=90, fontsize=7)
            ax.set_yticklabels(cls_names, fontsize=7)
            ax.set_xlabel("Prediksi", fontweight="bold")
            ax.set_ylabel("Aktual", fontweight="bold")
            ax.set_title(f"Confusion Matrix (Akurasi {best_run['metrics']['accuracy']:.2%})", pad=20)
            st.pyplot(fig)
            plt.close(fig)

    # TAB 5: LIVE RUNNER
    with tab_runner:
        st.subheader("5. Eksekusi Ulang Algoritma PSO")

        with st.container(border=True):
            st.markdown(
                "**Fungsi Utama Kode PSO Swarm Runner:**\n\n"
                "Fungsi berikut memicu eksekusi swarm partikel secara menggunakan data latih aktif "
                "dengan parameter partikel, iterasi, dan random seed yang dipilih:"
            )
            st.code(
                """# Eksekusi Algoritma PSO Swarm secara Langsung
global_best, global_score, history = optimize(
    engine=engine,
    active_train=train_active,
    targets=df_train["Kerusakan"].to_numpy(),
    rules=rules_raw,
    initial=initial_belief,
    seed=live_seed,
    particles=live_particles,
    iterations=live_iterations
)""",
                language="python",
            )
            st.caption(
                "Rujukan berkas: models/pso.ipynb (Cell 7) dan core/run_experiment.py (optimize)."
            )

        st.markdown(
            "Anda dapat menjalankan Particle Swarm Optimization secara langsung untuk membuktikan "
            "algoritma inferensi dan optimasi models/pso.ipynb bekerja secara nyata."
        )

        if not has_live_dataset:
            st.error("Silakan ekspor dataset di modul Preprocessing terlebih dahulu untuk menjalankan optimasi.")
        else:
            c_run1, c_run2, c_run3 = st.columns(3)
            live_seed = c_run1.number_input("Random Seed:", min_value=1, max_value=9999, value=48)
            live_particles = c_run2.slider("Jumlah Partikel:", min_value=5, max_value=40, value=15, step=5)
            live_iterations = c_run3.slider("Jumlah Iterasi:", min_value=5, max_value=50, value=20, step=5)

            if st.button("Jalankan Swarm Sekarang", type="primary"):
                prog = st.progress(0, text="Menginisialisasi swarm partikel...")
                with st.spinner(f"Mengoptimasi {live_particles} partikel selama {live_iterations} iterasi..."):
                    global_best, global_score, history = optimize(
                        engine,
                        train_active,
                        df_train["Kerusakan"].to_numpy(),
                        rules_raw,
                        initial_belief,
                        int(live_seed),
                        int(live_particles),
                        int(live_iterations),
                    )
                    prog.progress(100, text="Selesai.")

                live_probs = engine.matrix(test_active, global_best)
                live_eval = metrics(y_test, live_probs, classes)

                st.success(f"Optimasi Selesai. Fitness Latih: {global_score:.6f}")

                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Akurasi Uji", f"{live_eval['accuracy']:.2%}", f"{round(live_eval['accuracy']*len(y_test))}/{len(y_test)} benar")
                r2.metric("Macro F1", f"{live_eval['macro_f1']:.2%}")
                r3.metric("Weighted F1", f"{live_eval['weighted_f1']:.2%}")
                r4.metric("Brier Score", f"{live_eval['multiclass_brier']:.4f}")

                fig_l, ax_l = plt.subplots(figsize=(8, 3.5))
                ax_l.plot(history, color="#0284C7", lw=2, marker="o", markersize=3)
                ax_l.set_xlabel("Iterasi")
                ax_l.set_ylabel("Fitness (1 - Brier Latih)")
                ax_l.set_title(f"Konvergensi PSO Live (Seed {live_seed})")
                ax_l.grid(True, linestyle="--", alpha=0.5)
                st.pyplot(fig_l)
                plt.close(fig_l)
