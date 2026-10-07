"""
Service Preprocessing Dataset Deteksi Kerusakan iPhone.
Ditranskripsikan langsung dari models/preprocessing.ipynb untuk menjamin
reprodusibilitas 100% pada pemrosesan dataset.
"""

import datetime
import json
import re
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

SLANG_MAP = {
    r'\bbatrai\b': 'baterai',
    r'\bbatre\b': 'baterai',
    r'\bbatrey\b': 'baterai',
    r'\bbattery\b': 'baterai',
    r'\bbatarai\b': 'baterai',
    r'\bgembung\b': 'kembung',
    r'\blembung\b': 'kembung',
    r'\bgakbisa\b': 'tidak bisa',
    r'\bgkbisa\b': 'tidak bisa',
    r'\bgabisa\b': 'tidak bisa',
    r'\bgak bisa\b': 'tidak bisa',
    r'\bgk bisa\b': 'tidak bisa',
    r'\bga bisa\b': 'tidak bisa',
    r'\bkoncas\b': 'konektor cas',
    r'\bkon cas\b': 'konektor cas',
    r'\blubang cas\b': 'konektor cas',
    r'\bport cas\b': 'konektor cas',
    r'\bport charger\b': 'konektor cas',
    r'\bmatot\b': 'mati total',
    r'\bshort\b': 'korsleting',
    r'\bkonslet\b': 'korsleting',
    r'\bblkg\b': 'belakang',
    r'\bdicharge\b': 'dicas',
    r'\bdi charge\b': 'dicas',
    r'\bflexible\b': 'fleksibel',
    r'\bfleksi\b': 'fleksibel',
    r'\bflexy\b': 'fleksibel',
    r'\bflexyble\b': 'fleksibel',
    r'\bfelxyble\b': 'fleksibel',
    r'\bts\b': 'touchscreen',
    r'\blayar\b': 'lcd',
    r'\bscreen\b': 'lcd',
    r'\bcamera\b': 'kamera',
    r'\bbackdor\b': 'backdoor',
    r'\bbckdor\b': 'backdoor',
    r'\bback glass\b': 'backdoor',
    r'\bbackglass\b': 'backdoor',
    r'\bkaca belakang\b': 'backdoor',
    r'\bpunggung\b': 'backdoor',
    r'\bon off\b': 'on/off',
    r'\bonoff\b': 'on/off',
    r'\bbutton\b': 'tombol',
    r'\bbtn\b': 'tombol',
    r'\bcharge\b': 'cas',
    r'\bcharger\b': 'cas',
    r'\bathena\b': 'antena',
}


def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text)
    return re.sub(r'\s+', ' ', text).strip()


def match_keywords(text: str, keywords) -> bool:
    patterns = []
    for k in keywords:
        escaped = re.escape(k).replace(r'\ ', r'\s+')
        patterns.append(rf'\b{escaped}\b')
    pattern = '|'.join(patterns)
    return bool(re.search(pattern, text, re.IGNORECASE))


def map_row(row, wifi_reviews=None):
    if wifi_reviews is None:
        wifi_reviews = {}

    sym_text = str(row['Symptom_Text']).lower() + " " + str(row['Context_Text']).lower()
    act_text = str(row['Action_Text']).lower()

    # 1. Signal
    if match_keywords(sym_text, ['sinyal hilang', 'signal hilang', 'hilang jaringan', 'modem', 'baseband', 'no signal', 'keblokir']):
        signal = 'Hilang Total'
    elif match_keywords(sym_text, ['sinyal lemah', 'signal lemah', 'sinyal naik turun', 'signal hilang timbul']):
        signal = 'Bar Rendah'
    else:
        signal = 'Normal'

    # 2. Baterai
    if match_keywords(sym_text, ['baterai', 'kembung', 'drop', 'boros', 'mentok 0%', 'turun']):
        baterai = 'Daya Tahan Rendah/Gembung'
    else:
        baterai = 'Normal'

    # 3. LCD
    has_lcd_kw = match_keywords(sym_text, ['greenscreen', 'greenline', 'hijau'])
    has_gelap_kw = match_keywords(sym_text, ['blank', 'blackscreen', 'gelap', 'retak', 'garis', 'pecah']) and not match_keywords(sym_text, ['backdoor', 'kaca belakang', 'punggung', 'housing', 'casing', 'bodi'])
    has_pecah_general = match_keywords(sym_text, ['pecah']) and not match_keywords(sym_text, ['suara', 'speaker', 'audio', 'buzzer', 'backdoor', 'kaca belakang', 'punggung', 'housing', 'casing', 'bodi'])

    if has_lcd_kw:
        lcd = 'Greenscreen'
    elif has_gelap_kw or has_pecah_general:
        lcd = 'Gelap'
    else:
        lcd = 'Normal'

    # 4. Wifi
    if match_keywords(sym_text, ['wifi tidak bisa aktif', 'wifi tidak dapat aktif', 'wifi tidak bisa diaktifkan', 'wifi tidak dapat diaktifkan', 'toggle wifi abu abu', 'wifi greyed out']):
        wifi = 'Hilang Total/Tidak Dapat Diaktifkan'
    elif match_keywords(sym_text, ['wifi lemah', 'wifi putus', 'wifi hilang timbul', 'wifi tidak stabil']):
        wifi = 'Sinyal Lemah/Tidak Stabil'
    else:
        wifi = 'Normal'

    # 5. Touchscreen
    if match_keywords(sym_text, ['disentuh', 'sentuh', 'touchscreen', 'ghostouch', 'ngefreeze']):
        touch = 'Tidak bisa disentuh'
    else:
        touch = 'Normal'

    # 6. Tegangan
    if match_keywords(sym_text, ['korsleting', 'mati total', 'mati', 'korosi', 'basah', 'kena air', 'masuk air']):
        if match_keywords(sym_text, ['tombol', 'kamera', 'speaker', 'wifi']):
            tegangan = '0,8 - 2,2'
        else:
            tegangan = '0,0'
    elif match_keywords(sym_text, ['tegangan rendah', 'vcc main', 'baterai drop']):
        tegangan = '0,6'
    else:
        tegangan = '0,8 - 2,2'

    # 7. Kamera
    if match_keywords(sym_text, ['kamera', 'foto', 'lensa']) and match_keywords(sym_text, ['getar', 'goyang', 'vibrasi', 'vibration', 'ois']):
        kamera = 'Bergetar / OIS Tidak Stabil'
    elif match_keywords(sym_text, ['kamera', 'foto', 'buram', 'jamur']):
        kamera = 'Blank'
    else:
        kamera = 'Normal'

    # 8. Konektor Cas
    if match_keywords(sym_text, ['tidak bisa dicas', 'dicas mati', 'dicas tidak naik', 'dicas keluar masuk', 'konektor cas', 'dicas', 'cas', 'konektor']):
        if match_keywords(sym_text, ['keluar masuk', 'longgar', 'kotor']):
            konektor = 'Keluar masuk'
        else:
            konektor = 'Tidak Ngecas'
    else:
        konektor = 'Normal'

    # 9. Speaker
    has_speaker_kw = match_keywords(sym_text, ['speaker', 'earpiece', 'buzzer', 'nada', 'dering', 'audio']) or (match_keywords(sym_text, ['suara']) and not match_keywords(sym_text, ['mikrofon', 'microphone', 'mic', 'rekam', 'merekam', 'tidak dengar', 'orang tidak dengar', 'tidak terdengar']))
    has_pecah_speaker = match_keywords(sym_text, ['pecah']) and match_keywords(sym_text, ['suara', 'speaker', 'buzzer', 'audio']) and not match_keywords(sym_text, ['mikrofon', 'microphone', 'mic', 'rekam', 'merekam'])
    if has_speaker_kw or has_pecah_speaker:
        speaker = 'Rusak'
    else:
        speaker = 'Normal'

    # 9b. Mikrofon
    if match_keywords(sym_text, ['mikrofon', 'microphone', 'mic', 'rekam suara', 'merekam', 'recording', 'tidak terdengar', 'suara tidak terdengar', 'tidak dengar', 'orang tidak dengar', 'tidak kedengaran', 'suara tidak kedengaran', 'pihak lain tidak dengar', 'orang lain tidak dengar', 'suara tidak masuk', 'suara putus', 'telepon tidak terdengar']):
        mikrofon = 'Tidak Berfungsi'
    else:
        mikrofon = 'Normal'

    # 10. Backdoor
    if match_keywords(sym_text, ['backdoor', 'kaca belakang', 'punggung']):
        backdoor = 'Pecah/Retak'
    else:
        backdoor = 'Normal'

    # 10b. Housing
    if match_keywords(sym_text, ['housing', 'casing', 'bodi']):
        housing = 'Pecah/Retak/Bengkok'
    else:
        housing = 'Normal'

    # 11. Tombol
    if match_keywords(sym_text, ['tombol', 'power', 'volume', 'haptic', 'haptik', 'switch', 'silent', 'home', 'on off', 'on/off']):
        tombol = 'Tidak Berfungsi'
    else:
        tombol = 'Normal'

    # Target Label: Kerusakan (13 Kategori)
    damage = None
    if match_keywords(act_text, ['baterai', 'konektor baterai', 'soket baterai', 'fuse']):
        damage = 'Baterai Rusak'
    elif match_keywords(act_text, ['lcd', 'touchscreen', 'glass', 'sentuh', 'pindah chip', 'jalur lcd', 'lampu', 'display', 'screen', 'greenscreen', 'whitescreen', 'blackscreen', 'greenline']):
        damage = 'LCD Rusak'
    elif match_keywords(act_text, ['speaker', 'buzzer', 'earpiece', 'suara pecah']):
        damage = 'Speaker Rusak'
    elif match_keywords(act_text, ['ic power', 'vcc main', 'cpu', 'power', 'jalur vcc', 'mesin', 'jalur', 'short', 'korsleting', 'mati', 'mati total', 'mati cek', 'korosi', 'swap board']):
        damage = 'IC Power Rusak'
    elif match_keywords(act_text, ['ic cas', 'ic charger', 'ic charging', 'cas rusak', 'hydra']):
        damage = 'IC Cas Rusak'
    elif match_keywords(act_text, ['baseband', 'ic rf', 'ic signal', 'ic wtr', 'wtr', 'ic rf/baseband']):
        damage = 'IC WTR Rusak'
    elif match_keywords(act_text, ['antena sinyal', 'antena signal', 'fleksibel antena', 'sinyal', 'signal']):
        damage = 'Antena Signal Rusak'
    elif match_keywords(act_text, ['kamera', 'lens', 'flash', 'kamera depan', 'kamera belakang']):
        damage = 'Kamera Rusak'
    elif match_keywords(act_text, ['mikrofon', 'mic', 'microfon']):
        damage = 'Mikrofon Rusak'
    elif match_keywords(act_text, ['konektor cas', 'port cas', 'fleksibel cas', 'charger kotor', 'cas', 'konektor']):
        damage = 'Port Pengisian Rusak'
    elif match_keywords(act_text, ['ic audio', 'audio', 'audio rusak']):
        damage = 'IC Audio Rusak'
    elif match_keywords(act_text, ['backdoor', 'kaca belakang', 'punggung']):
        damage = 'Backdoor Rusak'
    elif match_keywords(act_text, ['housing', 'casing', 'bodi']):
        damage = 'Housing Rusak'
    elif match_keywords(act_text, ['tombol', 'power', 'volume', 'haptic', 'haptik', 'switch', 'silent', 'home', 'on off', 'on/off']):
        damage = 'Tombol Rusak'

    if damage is None and row['Source'] == 'Toko 2':
        if match_keywords(sym_text, ['baterai', 'soket baterai', 'konektor baterai', 'fuse']):
            damage = 'Baterai Rusak'
        elif match_keywords(sym_text, ['lcd', 'touchscreen', 'glass', 'sentuh', 'pindah chip', 'jalur lcd', 'lampu', 'display', 'screen', 'greenscreen', 'whitescreen', 'blackscreen', 'greenline']):
            damage = 'LCD Rusak'
        elif match_keywords(sym_text, ['speaker', 'buzzer', 'earpiece', 'suara pecah']):
            damage = 'Speaker Rusak'
        elif match_keywords(sym_text, ['ic power', 'vcc main', 'cpu', 'power', 'jalur vcc', 'mesin', 'jalur', 'short', 'korsleting', 'mati', 'mati total', 'mati cek', 'korosi', 'swap board']):
            damage = 'IC Power Rusak'
        elif match_keywords(sym_text, ['ic cas', 'ic charger', 'ic charging', 'cas rusak', 'hydra']):
            damage = 'IC Cas Rusak'
        elif match_keywords(sym_text, ['baseband', 'ic rf', 'ic signal', 'ic wtr', 'wtr', 'ic rf/baseband']):
            damage = 'IC WTR Rusak'
        elif match_keywords(sym_text, ['antena sinyal', 'antena signal', 'fleksibel antena', 'sinyal', 'signal']):
            damage = 'Antena Signal Rusak'
        elif match_keywords(sym_text, ['kamera', 'lens', 'flash', 'kamera depan', 'kamera belakang']):
            damage = 'Kamera Rusak'
        elif match_keywords(sym_text, ['mikrofon', 'mic', 'microfon']):
            damage = 'Mikrofon Rusak'
        elif match_keywords(sym_text, ['konektor cas', 'port cas', 'fleksibel cas', 'charger kotor', 'cas', 'konektor']):
            damage = 'Port Pengisian Rusak'
        elif match_keywords(sym_text, ['ic audio', 'audio', 'audio rusak']):
            damage = 'IC Audio Rusak'
        elif match_keywords(sym_text, ['backdoor', 'kaca belakang', 'punggung']):
            damage = 'Backdoor Rusak'
        elif match_keywords(sym_text, ['housing', 'casing', 'bodi']):
            damage = 'Housing Rusak'
        elif match_keywords(sym_text, ['tombol', 'power', 'volume', 'haptic', 'haptik', 'switch', 'silent', 'home', 'on off', 'on/off']):
            damage = 'Tombol Rusak'

    reviewed_wifi_case = wifi_reviews.get(f"{row['Tipe HP']}|{sym_text.strip()}")
    if reviewed_wifi_case:
        wifi = reviewed_wifi_case['wifi_value']
        damage = reviewed_wifi_case['damage_label']

    if damage is None:
        return None

    return pd.Series([row['Tipe HP'], signal, baterai, lcd, wifi, touch, tegangan, kamera, konektor, speaker, mikrofon, backdoor, housing, tombol, sym_text.strip(), damage])


def stratified_split(df, target_col='Kerusakan', test_size=0.2, random_state=42):
    counts = df[target_col].value_counts()
    rare_classes = counts[counts < 2].index.tolist()

    df_rare = df[df[target_col].isin(rare_classes)]
    df_normal = df[~df[target_col].isin(rare_classes)]

    df_train_normal, df_test_normal = train_test_split(
        df_normal,
        test_size=test_size,
        random_state=random_state,
        stratify=df_normal[target_col],
    )

    df_train = pd.concat([df_train_normal, df_rare], ignore_index=True)
    df_test = df_test_normal.reset_index(drop=True)
    df_train = df_train.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return df_train, df_test


def execute_full_preprocessing():
    """
    Menjalankan seluruh pipeline preprocessing dari data toko 2 & data utama,
    mengekspor file dataLatih dan dataUji, serta memperbarui model_schema.json.
    """
    toko_path = DATA_DIR / "data toko 2.xlsx"
    utama_path = DATA_DIR / "data utama.xlsx"
    expert_path = DATA_DIR / "expertDiagnosesAndFix.json"

    if not toko_path.is_file() or not utama_path.is_file():
        raise FileNotFoundError("File data mentah Excel tidak ditemukan di folder data/")

    df_jan = pd.read_excel(toko_path, sheet_name="JAN")
    df_feb = pd.read_excel(toko_path, sheet_name="FEB")
    df_toko = pd.concat([df_jan, df_feb], ignore_index=True)
    df_utama = pd.read_excel(utama_path, header=None)

    wifi_reviews = {}
    if expert_path.is_file():
        with open(expert_path, "r", encoding="utf-8") as expert_file:
            expert_db = json.load(expert_file)
            wifi_reviews = {
                f"{item['phone_type']}|{normalize_text(item['raw_text'])}": item
                for item in expert_db.get('dataset_curation', {}).get('wifi_reviewed_cases', [])
            }

    records = []
    # Bersihkan data toko 2
    for _, row in df_toko.iterrows():
        hp = str(row['TIPE HP']).upper()
        if 'IPHONE' not in hp:
            continue
        kerusakan = str(row['KERUSAKAN']).lower()
        sw_keywords = ['lupa pola', 'flash', 'sofware', 'software', 'instal ulang', 'icloud', 'cleaning', 'stuck logo', 'bypass']
        if any(k in kerusakan for k in sw_keywords):
            continue
        symptom_cleaned = kerusakan
        for verb in ['ganti ', 'servis ', 'lem ulang ', 'lem ', 'bersihkan ', 'cek ']:
            symptom_cleaned = symptom_cleaned.replace(verb, '')
        records.append({
            'Source': 'Toko 2',
            'Tipe HP': hp,
            'Symptom_Text': normalize_text(symptom_cleaned),
            'Context_Text': '',
            'Action_Text': normalize_text(kerusakan),
        })

    # Bersihkan data utama
    for idx, row in df_utama.iterrows():
        if idx == 0 and "Wahid Willy" in str(row[1]):
            continue
        hp = str(row[2]).upper()
        if 'IPHONE' not in hp:
            continue
        s1 = str(row[4]).lower()
        s2 = str(row[5]).lower()
        action = str(row[6]).lower()
        sw_keywords = ['lupa pola', 'flash', 'sofware', 'software', 'instal ulang', 'icloud', 'cleaning', 'stuck logo', 'bypass', 'downgrade']
        if any(k in s1 for k in sw_keywords) or any(k in s2 for k in sw_keywords) or any(k in action for k in sw_keywords):
            continue
        records.append({
            'Source': 'Utama',
            'Tipe HP': hp,
            'Symptom_Text': normalize_text(s1),
            'Context_Text': normalize_text(s2),
            'Action_Text': normalize_text(action),
        })

    df_raw = pd.DataFrame(records)

    mapped_records = []
    for _, row in df_raw.iterrows():
        res = map_row(row, wifi_reviews)
        if res is not None:
            mapped_records.append(res)

    df_mapped = pd.DataFrame(mapped_records)
    df_mapped.columns = [
        'Tipe HP', 'Signal', 'Baterai', 'LCD', 'Wifi', 'Touchscreen',
        'Tegangan', 'Kamera', 'Konektor Cas', 'Speaker', 'Mikrofon',
        'Backdoor', 'Housing', 'Tombol', 'Raw_Text', 'Kerusakan',
    ]

    df_train, df_test = stratified_split(df_mapped, 'Kerusakan', test_size=0.2, random_state=42)

    latih_dir = DATA_DIR / "dataLatih"
    uji_dir = DATA_DIR / "dataUji"
    latih_dir.mkdir(parents=True, exist_ok=True)
    uji_dir.mkdir(parents=True, exist_ok=True)

    # Simpan file dataset acuan (2026-08-29-20-08) agar hash dan eksperimen pso.ipynb cocok
    ref_train = latih_dir / "dataLatih-2026-08-29-20-08.csv"
    ref_test = uji_dir / "dataUji-2026-08-29-20-08.csv"
    df_train.to_csv(ref_train, index=False)
    df_test.to_csv(ref_test, index=False)

    # Simpan juga versi timestamp saat ini
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    ts_train = latih_dir / f"dataLatih-{timestamp}.csv"
    ts_test = uji_dir / f"dataUji-{timestamp}.csv"
    df_train.to_csv(ts_train, index=False)
    df_test.to_csv(ts_test, index=False)

    # Perbarui model_schema.json
    feature_columns = [col for col in df_train.columns if col not in ['Tipe HP', 'Raw_Text', 'Kerusakan']]
    df_schema = pd.concat([df_train, df_test], ignore_index=True)
    schema = {
        'version': f'dataset-{timestamp}',
        'feature_order': feature_columns,
        'allowed_values': {col: sorted(df_schema[col].dropna().astype(str).unique().tolist()) for col in feature_columns},
        'defaults': {col: str(df_train[col].mode().iloc[0]) for col in feature_columns},
        'dataset_size': {'train': int(len(df_train)), 'test': int(len(df_test))},
    }
    with open(DATA_DIR / 'model_schema.json', 'w', encoding='utf-8') as sf:
        json.dump(schema, sf, ensure_ascii=False, indent=2)

    return {
        'total_awal': len(df_utama) + len(df_toko),
        'hardware_lolos': len(df_raw),
        'terpetakan': len(df_mapped),
        'train_count': len(df_train),
        'test_count': len(df_test),
        'train_path': str(ref_train),
        'test_path': str(ref_test),
        'df_train': df_train,
        'df_test': df_test,
        'df_mapped': df_mapped,
    }
