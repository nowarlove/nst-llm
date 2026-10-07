#  05 - Skema Fitur & Basis Pengetahuan

Catatan ini mendokumentasikan taksonomi lengkap sistem pakar: 13 fitur teknis iPhone, 15 kelas target kerusakan, dan 19 aturan bukti (*evidence rules*) beserta perbandingan nilai *belief* awal vs hasil optimasi PSO.

Parent: [[00 - Index Utama (MOC)]]  
Terkait: [[02 - Teori & Mesin Dempster-Shafer]], [[03 - Optimasi Particle Swarm Optimization (PSO)]]

---

##  1. Daftar 13 Fitur Teknis & Nilai Valid

Seluruh fitur diturunkan langsung dari dataset penelitian ([`data/model_schema.json`](file:///e:/Deskop/deteksiKerusakanIphone/data/model_schema.json)):

| # | Nama Fitur | Nilai Default | Seluruh Nilai yang Diizinkan |
|---|---|---|---|
| 1 | `Signal` | `Normal` | `Bar Rendah`, `Hilang Total`, `Normal` |
| 2 | `Baterai` | `Normal` | `Daya Tahan Rendah/Gembung`, `Normal` |
| 3 | `LCD` | `Normal` | `Gelap`, `Greenscreen`, `Normal` |
| 4 | `Wifi` | `Normal` | `Hilang Total/Tidak Dapat Diaktifkan`, `Normal`, `Sinyal Lemah/Tidak Stabil` |
| 5 | `Touchscreen` | `Normal` | `Normal`, `Tidak bisa disentuh` |
| 6 | `Tegangan` | `0,8 - 2,2` | `0,0`, `0,6`, `0,8 - 2,2` (Ampere saat di-charge / DC power supply) |
| 7 | `Kamera` | `Normal` | `Bergetar / OIS Tidak Stabil`, `Blank`, `Normal` |
| 8 | `Konektor Cas` | `Normal` | `Keluar masuk`, `Normal`, `Tidak Ngecas` |
| 9 | `Speaker` | `Normal` | `Normal`, `Rusak` |
| 10| `Mikrofon` | `Normal` | `Normal`, `Tidak Berfungsi` |
| 11| `Backdoor` | `Normal` | `Normal`, `Pecah/Retak` |
| 12| `Housing` | `Normal` | `Normal`, `Pecah/Retak/Bengkok` |
| 13| `Tombol` | `Normal` | `Normal`, `Tidak Berfungsi` |

---

##  2. Daftar 15 Kelas Target Kerusakan & Prior Dataset

Berdasarkan 736 baris data latih historis:

| No | Kelas Kerusakan Hardware | Prior ($P$) | Karakteristik Klinis |
|---|---|---|---|
| 1 | `LCD Rusak` | $0.3302$ ($33.0\%$) | Layar mati, bergaris, blank, atau touchscreen tidak merespons |
| 2 | `Baterai Rusak` | $0.1875$ ($18.8\%$) | Baterai drop, gembung, atau mati mendadak saat persentase turun |
| 3 | `Port Pengisian Rusak` | $0.0924$ ($9.2\%$) | Kabel harus digoyang (*keluar masuk*), debu menumpuk, pin aus |
| 4 | `IC Power Rusak` | $0.0883$ ($8.8\%$) | Tegangan gantung ($0.0\text{A}$ atau $0.6\text{A}$), mati total (*short circuit*) |
| 5 | `Tombol Rusak` | $0.0802$ ($8.0\%$) | Tombol power/volume keras atau macet |
| 6 | `Backdoor Rusak` | $0.0679$ ($6.8\%$) | Kaca belakang pecah/retak akibat benturan |
| 7 | `Kamera Rusak` | $0.0462$ ($4.6\%$) | Kamera blank hitam atau OIS bergetar (*buzzing*) |
| 8 | `Speaker Rusak` | $0.0340$ ($3.4\%$) | Suara kresek-kresek, kecil, atau tidak ada suara telpon |
| 9 | `Housing Rusak` | $0.0326$ ($3.3\%$) | Rangka bodi melengkung, bengkok, atau retak parah |
| 10| `Antena Signal Rusak` | $0.0204$ ($2.0\%$) | Sinyal seluler lemah setelah ganti casing/jatuh |
| 11| `IC WTR Rusak` | $0.0082$ ($0.8\%$) | *Searching...* atau *No Service*, modem firmware hilang |
| 12| `Mikrofon Rusak` | $0.0041$ ($0.4\%$) | Lawan bicara tidak mendengar suara atau voice note kosong |
| 13| `Antena Wifi Rusak` | $0.0027$ ($0.3\%$) | Wifi sinyal lemah, hanya terhubung dekat router |
| 14| `IC Audio Rusak` | $0.0027$ ($0.3\%$) | Voice memo greyed out, speaker phone mati |
| 15| `IC Cas Rusak` | $0.0027$ ($0.3\%$) | *Fake charging* (lambang petir muncul tapi baterai tidak bertambah) |

---

## ️ 3. Perbandingan Matriks Belief: Pakar Awal vs Optimal PSO

Berikut adalah ringkasan perbandingan bobot belief awal pakar ([`data/belief.json`](file:///e:/Deskop/deteksiKerusakanIphone/data/belief.json)) dengan hasil optimasi PSO ([`data/optimal_knowledge_base.json`](file:///e:/Deskop/deteksiKerusakanIphone/data/optimal_knowledge_base.json)):

| Gejala Aktif | Hipotesis Kerusakan | Belief Pakar Awal | Optimal Belief (PSO) | Ketidakpastian ($\Theta$) |
|---|---|---|---|---|
| `Signal = Hilang Total` | IC WTR Rusak<br>Antena Signal Rusak | $0.70$<br>$0.20$ | **$0.2285$**<br>**$0.7215$** | $0.05$ |
| `Baterai = Daya Tahan Rendah/Gembung` | Baterai Rusak<br>IC Cas Rusak | $0.80$<br>$0.10$ | **$0.9500$**<br>**$0.0000$** | $0.05$ |
| `LCD = Gelap` | LCD Rusak<br>IC Power Rusak | $0.70$<br>$0.20$ | **$0.8659$**<br>**$0.0841$** | $0.05$ |
| `LCD = Greenscreen` | LCD Rusak | $0.85$ | **$0.9500$** | $0.05$ |
| `Wifi = Hilang Total/Tidak Dapat Diaktifkan`| IC Wifi / WTR<br>Antena Wifi | $0.80$<br>$0.10$ | **$0.9500$**<br>**$0.0000$** | $0.05$ |
| `Touchscreen = Tidak bisa disentuh` | LCD Rusak<br>IC Touch | $0.85$ | **$0.9500$** | $0.05$ |
| `Tegangan = 0,0` | IC Power Rusak<br>Baterai Rusak | $0.60$<br>$0.30$ | **$0.5517$**<br>**$0.3983$** | $0.05$ |
| `Kamera = Bergetar / OIS Tidak Stabil` | Kamera Rusak | $0.90$ | **$0.9500$** | $0.05$ |
| `Kamera = Blank` | Kamera Rusak | $0.85$ | **$0.9500$** | $0.05$ |
| `Konektor Cas = Keluar masuk` | Port Pengisian Rusak | $0.80$ | **$0.9500$** | $0.05$ |
| `Tombol = Tidak Berfungsi` | Tombol Rusak | $0.70$ | **$0.7410$** | **$0.2590$** |

> [!NOTE]
> Perhatikan pada gejala `Tombol = Tidak Berfungsi`: nilai ketidakpastian $\Theta$ relatif tinggi ($0.2590$). Hal ini mencerminkan realitas hardware bahwa tombol fisik tidak berfungsi bisa disebabkan oleh tombol mekanis itu sendiri, *flexible cable switch*, atau jalur *pull-up resistor* pada motherboard.
