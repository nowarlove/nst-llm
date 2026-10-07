# 02 - Teori & Mesin Dempster-Shafer

Catatan ini menguraikan landasan teori matematis **Dempster-Shafer Theory of Evidence** dan bagaimana teori tersebut diimplementasikan pada mesin inferensi di [`core/ds_engine.py`](file:///e:/Deskop/deteksiKerusakanIphone/core/ds_engine.py).

Parent: [[00 - Index Utama (MOC)]]  
Terkait: [[01 - Arsitektur & Alur Kerja Sistem]], [[03 - Optimasi Particle Swarm Optimization (PSO)]], [[05 - Skema Fitur & Basis Pengetahuan]]

---

##  1. Konsep Dasar Teori Bukti (Theory of Evidence)

Teori Dempster-Shafer (DS) adalah kerangka kerja matematika untuk penalaran dengan ketidakpastian (*reasoning under uncertainty*) yang memperluas teori probabilitas Bayesian dengan memungkinkan penetapan probabilitas pada himpunan bagian (*subsets*), bukan hanya peristiwa tunggal.

### A. Frame of Discernment ($\Theta$)
Himpunan semesta dari semua hipotesis yang saling lepas (*mutually exclusive*) dan tuntas (*exhaustive*). Dalam sistem ini, $\Theta$ terdiri dari **15 kelas kerusakan hardware iPhone**:

$$\Theta = \{ \text{LCD Rusak}, \text{Baterai Rusak}, \text{IC Power Rusak}, \dots, \text{Tombol Rusak} \}$$

Ukuran ruang hipotesis adalah $|\Theta| = 15$, sehingga himpunan kuasa (*power set*) $2^\Theta$ memiliki $2^{15} = 32.768$ kemungkinan kombinasi hipotesis.

### B. Fungsi Massa / Basic Probability Assignment (BPA / $m$)
Fungsi $m: 2^\Theta \to [0, 1]$ yang memenuhi:

1. $m(\emptyset) = 0$ (asumsi dunia tertutup)
2. $\sum_{A \subseteq \Theta} m(A) = 1$

Nilai $m(A)$ merepresentasikan ukuran kepercayaan yang dialokasikan *tepat* pada himpunan hipotesis $A$, bukan pada himpunan bagian dari $A$.

### C. Derajat Ketidakpastian ($\Theta$)
Jika suatu aturan memiliki nilai belief untuk hipotesis $H$, sisa massanya dialokasikan ke ketidaktahuan total (*total ignorance* / $\Theta$):

$$m(\Theta) = 1 - \sum_{H \subset \Theta} m(H)$$

---

##  2. Aturan Kombinasi Dempster (Dempster's Rule of Combination)

Ketika terdapat dua bukti independen dengan fungsi massa $m_1$ dan $m_2$, keduanya digabungkan melalui aturan kombinasi ortogonal (*orthogonal sum*):

$$m_{1,2}(A) = \frac{\sum_{X \cap Y = A} m_1(X) \cdot m_2(Y)}{1 - K}$$

di mana $K$ adalah **koefisien konflik** (*degree of conflict*):

$$K = \sum_{X \cap Y = \emptyset} m_1(X) \cdot m_2(Y)$$

### Penanganan Konflik Khusus ($K \ge 1.0$)
Jika dua bukti sepenuhnya saling bertentangan secara total ($K = 1.0$, pembagi menjadi nol), sistem menangani kondisi batas ini secara aman:

```python
if K >= 1.0:
    return {self.Theta: 1.0}, 1.0
```
Artinya sistem menyatakan ketidaktahuan total ($\Theta = 1.0$) dan mencatat konflik total pada dev log.

---

##  3. Belief ($Bel$) dan Plausibility ($Pl$)

Untuk setiap hipotesis tunggal $A = \{ d \}$ ($d \in \Theta$):

- **Belief ($Bel(A)$)**: Batas bawah probabilitas, yaitu jumlah massa yang sepenuhnya mendukung $A$:
  $$Bel(A) = \sum_{B \subseteq A} m(B)$$
- **Plausibility ($Pl(A)$)**: Batas atas probabilitas, yaitu jumlah massa yang tidak bertentangan dengan $A$:
  $$Pl(A) = \sum_{B \cap A \ne \emptyset} m(B) = 1 - Bel(\overline{A})$$
- Hubungan interval:
  $$Bel(A) \le P(A) \le Pl(A)$$

---

##  4. Transformasi Probabilitas Pignistik (BetP)

Untuk mengambil keputusan diagnosis akhir berupa ranking probabilitas per kelas, *Transferable Belief Model* (Smets) menggunakan **Pignistic Probability Transformation ($BetP$)**:

$$BetP(c) = \sum_{c \in A \subseteq \Theta} \frac{m(A)}{|A|}$$

Karena dalam basis pengetahuan sistem ini setiap aturan $m(H)$ adalah hipotesis singleton ($|H|=1$), persamaan ini disederhanakan secara elegan:

$$BetP(c) = m(\{c\}) + \frac{m(\Theta)}{|\Theta|}$$

Di mana setiap kelas kerusakan $c$ mendapatkan bagian merata dari sisa ketidakpastian massa $m(\Theta)$ dibagi jumlah kelas ($|\Theta| = 15$).

---

## 5. Bedah Kode `core/ds_engine.py`

Berikut komponen kunci pada kelas `DSEngine`:

### 1. Inisialisasi & Validasi Prior
```python
def __init__(self, knowledge_base: dict):
    self.rules = knowledge_base['rules']
    raw_priors = knowledge_base['class_priors']
    prior_total = sum(float(value) for value in raw_priors.values())
    self.prior_was_normalized = abs(prior_total - 1.0) > 1e-9
    self.priors = {name: float(value) / prior_total for name, value in raw_priors.items()}
    self.all_damages = sorted(self.priors.keys())
    self.Theta = frozenset(self.all_damages)
    self.num_classes = len(self.all_damages)
```
- Menormalisasi *class priors* jika penjumlahannya tidak persis 1.0.
- Membangun `self.Theta` dari 15 kelas kerusakan.
- Memvalidasi bahwa setiap bobot belief pada aturan berada dalam rentang valid $[0, 1]$ dan $\sum b \le 1.0$.

### 2. Fungsi Penggabungan Dua Bukti `_combine_two`
```python
def _combine_two(self, m1: dict, m2: dict):
    m_new = {}
    K = 0.0
    for x, w1 in m1.items():
        for y, w2 in m2.items():
            inter = x.intersection(y)
            if not inter:
                K += w1 * w2
            else:
                m_new[inter] = m_new.get(inter, 0.0) + w1 * w2
    if K >= 1.0:
        return {self.Theta: 1.0}, 1.0
    for k in m_new:
        m_new[k] /= (1.0 - K)
    return m_new, K
```

### 3. Eksekusi Inferensi `run_inference(features)`
1. **Pencarian Aturan Aktif**: Membandingkan 13 nilai fitur input dengan 19 aturan evidence.
2. **Fallback Mode**: Jika tidak ada aturan yang cocok sama sekali (misal seluruh fitur bernilai `Normal`), sistem mengaktifkan fallback ke *class priors* dataset.
3. **Iterative Combination**: Menggabungkan mass function aturan aktif satu per satu dari bukti pertama hingga bukti terakhir.
4. **Perhitungan BetP, Bel, dan Pl**: Menghasilkan probabilitas pignistik terurut dari probabilitas tertinggi hingga terendah.
