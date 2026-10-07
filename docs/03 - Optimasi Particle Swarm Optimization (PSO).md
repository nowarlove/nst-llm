# 03 - Optimasi Particle Swarm Optimization (PSO)

Catatan ini mendokumentasikan bagaimana **Particle Swarm Optimization (PSO)** digunakan untuk mengoptimalkan bobot *belief* dalam basis pengetahuan Dempster-Shafer berdasarkan data latih penelitian hardware iPhone.

Parent: [[00 - Index Utama (MOC)]]  
Terkait: [[02 - Teori & Mesin Dempster-Shafer]], [[05 - Skema Fitur & Basis Pengetahuan]], [[07 - Panduan Eksperimen & Evaluasi Penelitian]]

---

## 1. Latar Belakang & Motivasi

Dalam sistem pakar klasik Dempster-Shafer, nilai *belief* ($m(H)$) ditentukan secara subjektif oleh pakar manusia (misalnya seorang teknisi senior memperkirakan $0.8$ untuk LCD rusak). Namun:
1. Estimasi subjektif manusia rentan bias.
2. Interaksi antar banyak bukti yang digabungkan berulang kali dapat menurunkan performa klasifikasi global.
3. **Solusi DS-PSO**: Nilai belief pakar awal ([`data/belief.json`](file:///e:/Deskop/deteksiKerusakanIphone/data/belief.json)) dijadikan posisi awal (*seed*), lalu dioptimalkan oleh PSO menggunakan 736 baris data latih historis riil agar mencapai akurasi dan kalibrasi probabilitas terbaik.

---

## 2. Representasi Partikel & Batasan (Constraints)

- **Dimensi Partikel ($D$)**: Setiap dimensi merepresentasikan bobot belief hipotesis pada aturan relasi gejala-kerusakan.
- **Vektor Posisi ($X_i$)**:
  $$X_i = [b_1, b_2, \dots, b_D]$$
- **Batasan Ruang Pencarian (Clipping Constraints)**:
  Sesuai aturan teori Dempster-Shafer, probabilitas massa tidak boleh negatif dan total belief pada suatu aturan tidak boleh melebihi $1.0$. Pada kode [`core/run_experiment.py`](file:///e:/Deskop/deteksiKerusakanIphone/core/run_experiment.py):

```python
def constrain(vector, rules):
    result = np.clip(np.asarray(vector, dtype=float), 0.0, 0.95)
    index = 0
    for rule in rules:
        size = len(rule["hypotheses"])
        values = result[index:index + size]
        total = values.sum()
        if total > 0.95:
            result[index:index + size] = values / total * 0.95
        index += size
    return result
```

> [!IMPORTANT]
> Batas maksimum total belief per aturan dibatasi pada **$0.95$**. Hal ini memastikan selalu ada sisa ketidakpastian massa minimal $m(\Theta) \ge 0.05$ agar mesin Dempster-Shafer tidak mengalami *overconfidence* / *zero uncertainty trap*.

---

## 3. Fungsi Kebugaran (Fitness Function)

Fitness function dirancang untuk memaksimalkan akurasi sekaligus menghargai kalibrasi probabilitas pignistik menggunakan **Multiclass Brier Score**:

$$\text{Brier Score} = \frac{1}{N} \sum_{i=1}^{N} \sum_{c=1}^{C} (P_{ic} - Y_{ic})^2$$

$$\text{Fitness}(X) = 1.0 - \text{Brier Score}$$

- $N$: Jumlah sampel data latih ($736$).
- $C$: Jumlah kelas kerusakan ($15$).
- $P_{ic}$: Probabilitas pignistik prediksi untuk kelas $c$ pada sampel $i$.
- $Y_{ic}$: Label ground truth *one-hot* ($1$ jika benar, $0$ jika salah).

Jika model memprediksi $100\%$ tepat pada kelas yang benar dengan probabilitas $1.0$, maka $\text{Brier Score} = 0$, sehingga $\text{Fitness} = 1.0$.

---

## 4. Formulasi Pergerakan Partikel

Pada setiap iterasi $t \in [1, T]$:

### 1. Bobot Inersia Dinamis (*Inertia Weight Damping*)
$$w(t) = 0.9 - 0.5 \times \frac{t}{T}$$
- Pada iterasi awal ($w \approx 0.9$), partikel melakukan eksplorasi luas (*global exploration*).
- Pada iterasi akhir ($w \approx 0.4$), partikel melakukan eksploitasi terfokus di sekitar posisi terbaik (*local exploitation*).

### 2. Pembaruan Kecepatan (*Velocity Update*)
$$V_i^{(t+1)} = \text{clip}\left( w(t) V_i^{(t)} + c_1 r_1 (P_{best, i} - X_i^{(t)}) + c_2 r_2 (G_{best} - X_i^{(t)}), -0.2, 0.2 \right)$$

- $c_1 = 2.0$: Parameter percepatan kognitif (*personal best*).
- $c_2 = 2.0$: Parameter percepatan sosial (*global best*).
- $r_1, r_2 \sim U(0, 1)$: Bilangan acak seragam.
- Kecepatan dibatasi dalam interval $[-0.2, 0.2]$ untuk mencegah ledakan partikel (*velocity explosion*).

### 3. Pembaruan Posisi (*Position Update*)
$$X_i^{(t+1)} = \text{constrain}(X_i^{(t)} + V_i^{(t+1)})$$

---

## 5. Optimasi Performa: Matrix & Combination Caching

Inferensi Dempster-Shafer berulang untuk puluhan partikel dan ratusan iterasi pada ratusan data latih memerlukan jutaan operasi perkalian himpunan. Skrip eksperimen mengimplementasikan teknik **caching kombinasi gejala**:

```python
def matrix(self, active_rows, beliefs):
    cache = {}
    rows = []
    for active in active_rows:
        signature = tuple(offset for offset, _ in active)
        if signature not in cache:
            cache[signature] = self.probabilities(active, beliefs)
        rows.append(cache[signature])
    return np.vstack(rows)
```

Banyak sampel dalam dataset memiliki kombinasi gejala aktif yang persis sama. Dengan mencatat hasil kalkulasi per *signature*, waktu eksekusi optimasi PSO dapat dipersingkat hingga **10x lebih cepat** tanpa mengubah hasil matematis sedikit pun.
