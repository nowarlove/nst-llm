# 06 - Layanan Bisnis dan Arsitektur Servis

Catatan ini mendokumentasikan modul logika bisnis, manajemen basis pengetahuan klinis, dan kebijakan keyakinan (confidence policy) pada model inferensi.

Parent: [[00 - Index Utama (MOC)]]  
Terkait: [[01 - Arsitektur & Alur Kerja Sistem]], [[02 - Teori & Mesin Dempster-Shafer]], [[05 - Skema Fitur & Basis Pengetahuan]]

---

## 1. Modul Pengetahuan Klinis (Clinical Knowledge)

Logika bisnis dan estimasi perbaikan diorganisasi sebagai modul Python murni di [`core/clinical_knowledge.py`](file:///e:/Deskop/deteksiKerusakanIphone/core/clinical_knowledge.py):

1. **`build_clinical_knowledge()`**:
   - Menyediakan metadata klinis untuk 15 kelas kerusakan iPhone (prosedur perbaikan, tingkat urgensi, serta estimasi biaya dasar per komponen).
2. **`apply_dynamic_price(knowledge, iphone_model)`**:
   - Menyesuaikan estimasi biaya perbaikan berdasarkan generasi perangkat (misal: seri Pro/Pro Max memiliki pengali harga suku cadang yang lebih tinggi).
3. **`selected_knowledge_base_path()`**:
   - Menentukan model inferensi aktif (prioritas pada `data/optimal_knowledge_base.json` hasil optimasi PSO, dengan fallback ke `data/belief.json`).

---

## 2. Kebijakan Keyakinan (Confidence Policy)

Untuk meningkatkan keandalan diagnosis, hasil kombinasi massa dievaluasi berdasarkan 3 parameter:
1. Probabilitas tertinggi ($P_{\text{top}}$)
2. Derajat ketidakpastian massa ($m(\Theta)$)
3. Ada tidaknya konflik antar bukti ($K > 0$)

```python
def evaluate_confidence(result):
    top_prob = result.get('top_probability', 0.0)
    uncertainty = result.get('uncertainty_theta', 0.0)
    has_conflict = any(step.get('conflict_k', 0.0) > 0 for step in result.get('dev_log', {}).get('conflict_steps', []))
    
    if top_prob < 0.50 or uncertainty >= 0.20 or has_conflict:
        return {
            'status': 'technician_review',
            'requires_technician': True,
            'reason': 'Probabilitas rendah, bukti berkonflik, atau ketidakpastian tinggi.'
        }
    return {
        'status': 'high_confidence',
        'requires_technician': False,
        'reason': 'Hasil diagnosis memiliki kepastian matematis tinggi.'
    }
```

Jika kasus ditandai `technician_review`, antarmuka menyarankan pemeriksaan fisik lebih lanjut oleh teknisi.

---

## 3. Integrasi Antarmuka

Antarmuka aplikasi berfokus pada Streamlit Hub ([`app.py`](file:///e:/Deskop/deteksiKerusakanIphone/app.py)) yang menjalankan alur pemrosesan data dan validasi model penelitian (`models/preprocessing.ipynb` dan `models/pso.ipynb`).
