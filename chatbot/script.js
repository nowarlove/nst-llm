// =============================================================================
// KONFIGURASI DAN BASIS PENGETAHUAN MODEL
// =============================================================================
const API_CONFIG = {
  baseUrl: "https://ai.sumopod.com/v1/chat/completions",
  apiKey: "//apikey",
  model: "gpt-4o-mini",
};

// Basis Pengetahuan Resmi Hasil Perhitungan Model & Pakar (15 Kelas Kerusakan + Software Gate)
const KNOWLEDGE_BASE_SYSTEM_PROMPT = `Anda adalah Asisten Konsultasi Teknis Servis iPhone resmi dari NST Phoneshop.

PRINSIP UTAMA:
Seluruh konsultasi, analisis gejala, diagnosis kerusakan, tindakan perbaikan, dan estimasi biaya WAJIB bersumber 100% dari basis pengetahuan model teknis iPhone di bawah ini. AI bertindak murni sebagai komunikator customer service yang menyajikan pengetahuan hasil model, BUKAN untuk mengarang diagnosis atau harga sendiri.

DAFTAR 15 KELAS KERUSAKAN HARDWARE RESMI, PROSEDUR & BIAYA:
1. LCD Rusak:
   - Gejala: Layar blank, bergaris (hijau/putih), greenscreen, layar retak/pecah, touchscreen tidak bisa disentuh atau ghost touch.
   - Bobot Belief Model: 95.0% pada gejala greenscreen, touchscreen macet; 86.6% pada layar gelap.
   - Solusi: Penggantian modul LCD screen (OLED/LCD sesuai seri).
   - Estimasi Biaya: Rp 400.000 - Rp 2.500.000 (iPhone 8/SE: 400k-600k; X/XS/11: 500k-1.2jt; 12/13: 900k-1.5jt; 14/15 Pro: 1.5jt-2.5jt).
   - Waktu Pengerjaan: 30 - 60 menit.

2. Baterai Rusak:
   - Gejala: Baterai cepat habis/drop, baterai kembung (layar terangkat), mendadak mati saat baterai 20-30%, battery health service.
   - Bobot Belief Model: 95.0% pada daya tahan rendah/kembung.
   - Solusi: Penggantian baterai berkualitas tinggi + kalibrasi siklus daya.
   - Estimasi Biaya: Rp 250.000 - Rp 750.000.
   - Waktu Pengerjaan: 30 - 60 menit.

3. Port Pengisian Rusak:
   - Gejala: Tidak bisa dicas, kabel charger longgar/keluar-masuk, harus ditekuk pada sudut tertentu agar mengisi.
   - Bobot Belief Model: 95.0% pada tidak ngecas; 79.7% pada konektor longgar.
   - Solusi: Pembersihan pin konektor atau pergantian fleksibel port charger (Lightning/USB-C).
   - Estimasi Biaya: Rp 100.000 - Rp 450.000.
   - Waktu Pengerjaan: 20 - 45 menit.

4. IC Cas Rusak (Hydra / Tristar):
   - Gejala: Indikator cas muncul tapi baterai tidak bertambah (fake charging), dicas malah berkurang, cepat panas saat dicas.
   - Solusi: Analisis skematik motherboard dan penggantian chip IC charging controller (Tristar/Hydra).
   - Estimasi Biaya: Rp 250.000 - Rp 700.000.
   - Waktu Pengerjaan: 1 - 4 jam.

5. IC Power Rusak (PMIC):
   - Gejala: iPhone mati total arus 0,0A (tidak merespon power supply), korsleting / short arus tinggi (0,6A ke atas) dan motherboard panas.
   - Bobot Belief Model: 71.5% pada arus 0,0A; 82.6% pada arus gantung/short 0,6A.
   - Solusi: Pengukuran jalur VDD Main/BATT, reballing atau penggantian chip Power Management IC (PMIC).
   - Estimasi Biaya: Rp 400.000 - Rp 1.200.000.
   - Waktu Pengerjaan: 3 - 8 jam.

6. Speaker Rusak:
   - Gejala: Suara speaker bawah atau earpiece telepon kresek-kresek, pecah, atau mati saat memutar musik/nada dering.
   - Bobot Belief Model: 89.5% pada speaker suara rusak.
   - Solusi: Penggantian modul speaker buzzer bawah atau modul earpiece atas.
   - Estimasi Biaya: Rp 100.000 - Rp 400.000.
   - Waktu Pengerjaan: 20 - 45 menit.

7. IC Audio Rusak:
   - Gejala: Semua fungsi audio mati bersamaan (speaker, mic, perekam suara / voice memo tombol rekam abu-abu atau macet, telepon tidak bersuara dua arah).
   - Solusi: Reballing atau jumper jalur pad micro-crack pada chip Audio Codec (sering terjadi pada iPhone 7, 8, dan seri X).
   - Estimasi Biaya: Rp 300.000 - Rp 800.000.
   - Waktu Pengerjaan: 2 - 5 jam.

8. Mikrofon Rusak:
   - Gejala: Suara telepon tidak terdengar oleh lawan bicara, namun speaker dapat mengeluarkan suara dengan normal.
   - Bobot Belief Model: 77.8% pada mikrofon tidak berfungsi.
   - Solusi: Penggantian fleksibel modul mikrofon (terintegrasi pada fleksibel port charger atau fleksibel kamera depan).
   - Estimasi Biaya: Rp 150.000 - Rp 500.000.
   - Waktu Pengerjaan: 30 - 60 menit.

9. Kamera Rusak:
   - Gejala: Kamera blank hitam saat dibuka, tidak bisa fokus, bergetar kencang (OIS stabilizer rusak), atau muncul bercak noda.
   - Bobot Belief Model: 95.0% pada kamera blank atau bergetar.
   - Solusi: Penggantian modul kamera belakang atau depan.
   - Estimasi Biaya: Rp 300.000 - Rp 1.500.000.
   - Waktu Pengerjaan: 30 - 90 menit.

10. IC WTR Rusak (Baseband Transceiver):
    - Gejala: Sinyal hilang total (Mencari / Searching / No Service), IMEI hilang saat ketik *#06#, atau tombol Wi-Fi berwarna abu-abu (greyed out).
    - Bobot Belief Model: 51.7% pada Wi-Fi hilang total; 22.9% pada sinyal hilang total.
    - Solusi: Pengecekan jalur tegangan baseband, reballing chip Baseband WTR RF Transceiver.
    - Estimasi Biaya: Rp 450.000 - Rp 1.000.000.
    - Waktu Pengerjaan: 3 - 6 jam.

11. Antena Signal Rusak:
    - Gejala: Sinyal sangat lemah (hanya 1 bar), sinyal sering putus di dalam ruangan padahal perangkat lain normal.
    - Bobot Belief Model: 72.2% pada gangguan sinyal antena.
    - Solusi: Pengecekan soket antena pada motherboard atau pergantian kabel antena seluler.
    - Estimasi Biaya: Rp 50.000 - Rp 350.000.
    - Waktu Pengerjaan: 30 menit - 2 jam.

12. Antena Wifi Rusak:
    - Gejala: Sinyal Wi-Fi lemah jika berjarak lebih dari 2 meter dari router, koneksi Bluetooth terputus-putus.
    - Bobot Belief Model: 95.0% pada sinyal Wi-Fi lemah/tidak stabil.
    - Solusi: Penggantian fleksibel modul antena Wi-Fi/Bluetooth.
    - Estimasi Biaya: Rp 150.000 - Rp 450.000.
    - Waktu Pengerjaan: 30 - 90 menit.

13. Backdoor Rusak:
    - Gejala: Kaca bodi penutup bagian belakang retak atau pecah akibat benturan.
    - Bobot Belief Model: 90.7% pada backdoor pecah.
    - Solusi: Penggantian kaca belakang menggunakan mesin laser pemisah lem kaca atau pergantian backdoor.
    - Estimasi Biaya: Rp 150.000 - Rp 800.000.
    - Waktu Pengerjaan: 1 - 3 jam.

14. Housing Rusak:
    - Gejala: Rangka bodi iPhone bengkok, penyok parah di sudut, atau patah.
    - Bobot Belief Model: 95.0% pada housing pecah/bengkok.
    - Solusi: Pemindahan seluruh komponen mesin ke casing/housing baru presisi.
    - Estimasi Biaya: Rp 200.000 - Rp 1.500.000.
    - Waktu Pengerjaan: 2 - 6 jam.

15. Tombol Rusak:
    - Gejala: Tombol Power, Volume atas/bawah, atau switch Mute macet, keras, atau tidak merespon saat ditekan.
    - Bobot Belief Model: 76.3% pada tombol fisik tidak berfungsi.
    - Solusi: Penggantian fleksibel sakelar tombol fisik.
    - Estimasi Biaya: Rp 100.000 - Rp 500.000.
    - Waktu Pengerjaan: 30 - 60 menit.

ATURAN GERBANG SOFTWARE (BUKAN KERUSAKAN HARDWARE):
Jika pelanggan mengeluhkan gejala seperti:
- Stuck pada logo Apple (bootloop berulang)
- Lupa passcode / pola / iPhone dinonaktifkan
- Gagal update iOS / penyimpanan penuh mendadak mati
-> Diagnosis: Masalah Perangkat Lunak (iOS Software). BUKAN kerusakan komponen hardware fisik.
-> Solusi: Flashing ulang via iTunes atau 3uTools dengan mode DFU / Recovery. Estimasi biaya jasa: Rp 50.000 - Rp 100.000.

PEDOMAN FORMAT JAWABAN KEPADA PELANGGAN:
1. Sapa pelanggan dengan ramah dan profesional tanpa menggunakan emoji sama sekali.
2. Jelaskan Ringkasan Analisis Gejala berdasarkan keluhan yang disampaikan.
3. Sebutkan Diagnosis Kerusakan Utama (beserta alternatif jika ada) sesuai hasil model Dempster-Shafer.
4. Berikan Tindakan Perbaikan yang tepat sesuai prosedur resmi teknisi.
5. Sebutkan Estimasi Biaya Resmi dan Estimasi Waktu Pengerjaan dari data di atas.
6. Ajak pelanggan untuk membawa unit ke toko NST Phoneshop untuk pengecekan fisik gratis oleh teknisi kami.
7. Jika informasi tipe iPhone atau gejala masih ambigu, tanyakan keluhan pendukung secara sopan.
8. DILARANG KERAS mengarang harga, estimasi waktu, atau nama kerusakan di luar ketentuan di atas.`;

// =============================================================================
// ENGINE FALLBACK LOKAL (JIKA KONEKSI API OFFLINE / GAGAL)
// =============================================================================
function runLocalKnowledgeDiagnosis(userText) {
  const t = userText.toLowerCase();

  // 1. Software Gate Check
  if (t.includes("bootloop") || t.includes("stuck logo") || t.includes("logo apple") || t.includes("lupa sandi") || t.includes("passcode") || t.includes("dinonaktifkan")) {
    return `Berdasarkan analisis model sistem kami, keluhan yang Anda sampaikan terindikasi sebagai Masalah Perangkat Lunak (iOS Software Issue), bukan kerusakan hardware fisik.

Diagnosis: Gangguan Sistem Operasi iOS (Bootloop / System Crash)
Tindakan Rekomendasi: Flashing ulang sistem melalui DFU / Recovery Mode menggunakan iTunes atau 3uTools.
Estimasi Biaya Jasa: Rp 50.000 - Rp 100.000
Estimasi Waktu Pengerjaan: 20 - 40 menit

Silakan bawa unit ke NST Phoneshop agar teknisi kami dapat melakukan pemulihan sistem tanpa risiko kegagalan firmware.`;
  }

  // 2. LCD Rusak
  if (t.includes("layar") || t.includes("lcd") || t.includes("screen") || t.includes("greenscreen") || t.includes("garis") || t.includes("touchscreen") || t.includes("sentuh")) {
    return `Berdasarkan analisis model inferensi Dempster-Shafer, gejala yang Anda alami mengarah pada:

Diagnosis Utama: LCD Rusak (Tingkat Keyakinan Model: 86.6% - 95.0%)
Penyebab Umum: Tekanan fisik, benturan jatuh, atau kerusakan jalur display OLED/LCD.
Tindakan Rekomendasi: Penggantian modul layar LCD/OLED baru berkualitas.
Estimasi Biaya: Rp 400.000 - Rp 2.500.000 (menyesuaikan tipe iPhone Anda).
Estimasi Waktu: 30 - 60 menit.

Silakan bawa iPhone Anda ke workshop NST Phoneshop untuk pemeriksaan fisik langsung.`;
  }

  // 3. Baterai Rusak
  if (t.includes("baterai") || t.includes("batre") || t.includes("battery") || t.includes("drop") || t.includes("kembung") || t.includes("boros")) {
    return `Berdasarkan basis data model diagnostik:

Diagnosis Utama: Baterai Rusak (Tingkat Keyakinan Model: 95.0%)
Penyebab Umum: Penurunan kapasitas kimiawi sel baterai (degradasi siklus) atau penggunaan charger non-standar.
Tindakan Rekomendasi: Penggantian baterai bergaransi dan kalibrasi sistem daya.
Estimasi Biaya: Rp 250.000 - Rp 750.000
Estimasi Waktu: 30 - 60 menit.

Kami menyediakan baterai pengganti berkualitas dengan pengujian daya langsung di toko.`;
  }

  // 4. Konektor Cas / IC Cas
  if (t.includes("cas") || t.includes("charge") || t.includes("charger") || t.includes("konektor") || t.includes("port cas")) {
    if (t.includes("tidak bertambah") || t.includes("berkurang") || t.includes("fake")) {
      return `Berdasarkan analisis gejala pengisian:

Diagnosis Utama: IC Cas Rusak / Hydra Tristar
Penyebab Umum: Kerusakan chip pengatur arus pengisian pada motherboard.
Tindakan Rekomendasi: Penggantian IC Charger controller pada logic board.
Estimasi Biaya: Rp 250.000 - Rp 700.000
Estimasi Waktu: 1 - 4 jam.`;
    }
    return `Berdasarkan analisis model inferensi:

Diagnosis Utama: Port Pengisian Rusak (Tingkat Keyakinan: 79.7% - 95.0%)
Penyebab Umum: Korosi pin kuningan, penumpukan kotoran/debu, atau pin fleksibel aus.
Tindakan Rekomendasi: Pembersihan pin konektor atau penggantian fleksibel port charger.
Estimasi Biaya: Rp 100.000 - Rp 450.000
Estimasi Waktu: 20 - 45 menit.`;
  }

  // 5. Mati Total / IC Power
  if (t.includes("matot") || t.includes("mati total") || t.includes("konslet") || t.includes("short") || t.includes("panas")) {
    return `Berdasarkan model evaluasi tegangan dan arus:

Diagnosis Utama: IC Power Rusak (PMIC) (Tingkat Keyakinan: 71.5% - 82.6%)
Diagnosis Alternatif: Baterai Rusak / Konsleting Jalur Utama VDD.
Tindakan Rekomendasi: Pengukuran jalur tegangan motherboard menggunakan power supply dan multitester, dilanjutkan reballing/ganti IC Power.
Estimasi Biaya: Rp 400.000 - Rp 1.200.000
Estimasi Waktu: 3 - 8 jam.`;
  }

  // 6. Sinyal / Wi-Fi
  if (t.includes("sinyal") || t.includes("signal") || t.includes("mencari") || t.includes("searching") || t.includes("no service") || t.includes("wifi")) {
    if (t.includes("searching") || t.includes("mencari") || t.includes("hilang total") || t.includes("imei")) {
      return `Berdasarkan basis pengetahuan model:

Diagnosis Utama: IC WTR Rusak (Baseband Transceiver)
Penyebab Umum: Retak solder ball akibat benturan pada chip Baseband logic board.
Tindakan Rekomendasi: Reballing atau servis jalur sinyal baseband.
Estimasi Biaya: Rp 450.000 - Rp 1.000.000
Estimasi Waktu: 3 - 6 jam.`;
    }
    return `Berdasarkan basis pengetahuan model:

Diagnosis: Antena Sinyal / Antena Wi-Fi Rusak (Tingkat Keyakinan: 72.2% - 95.0%)
Tindakan Rekomendasi: Penggantian modul fleksibel antena koaksial.
Estimasi Biaya: Rp 50.000 - Rp 450.000
Estimasi Waktu: 30 menit - 2 jam.`;
  }

  // 7. Kamera
  if (t.includes("kamera") || t.includes("camera") || t.includes("lens") || t.includes("getar")) {
    return `Berdasarkan analisis model:

Diagnosis Utama: Kamera Rusak (Tingkat Keyakinan: 95.0%)
Penyebab: Kerusakan modul sensor atau mekanisme OIS (Optical Image Stabilization) akibat getaran motor/benturan.
Tindakan Rekomendasi: Penggantian modul kamera.
Estimasi Biaya: Rp 300.000 - Rp 1.500.000
Estimasi Waktu: 30 - 90 menit.`;
  }

  // 8. Suara / Speaker / Mic
  if (t.includes("speaker") || t.includes("suara") || t.includes("kresek") || t.includes("mikrofon") || t.includes("mic")) {
    return `Berdasarkan analisis gejala audio:

Diagnosis: Speaker Rusak (89.5%) atau Mikrofon Rusak (77.8%)
Catatan: Jika semua fungsi audio (speaker, mic, perekam suara) mati bersamaan, indikasi mengarah ke IC Audio Codec.
Tindakan Rekomendasi: Penggantian modul speaker / mikrofon atau reballing IC Audio.
Estimasi Biaya: Rp 100.000 - Rp 500.000 (Modul) / Rp 300.000 - Rp 800.000 (IC Audio)
Estimasi Waktu: 30 menit - 3 jam.`;
  }

  // Default Clarification
  return `Terima kasih telah berkonsultasi. Untuk memberikan diagnosis yang tepat sesuai basis data model kami, mohon informasikan:
1. Tipe seri iPhone yang Anda gunakan (misal: iPhone 11, iPhone 13 Pro).
2. Gejala spesifik yang terjadi (apakah pada layar, baterai, pengisian daya, sinyal, audio, kamera, atau mati total).
3. Kejadian awal sebelum masalah timbul (seperti pernah terjatuh, terkena cairan, atau saat sedang dicas).

Kami siap memberikan rincian solusi dan estimasi biaya resmi sesuai keluhan Anda.`;
}

// =============================================================================
// LOGIKA ANTARMUKA CHATBOT
// =============================================================================
const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");

const chatHistory = [];
const initialInputHeight = messageInput.scrollHeight;

// Membuat elemen pesan
const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

// Menghasilkan respon bot
const generateBotResponse = async (incomingMessageDiv, userMessageText) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  // Tambahkan pesan user ke histori percakapan OpenAI format
  chatHistory.push({
    role: "user",
    content: userMessageText,
  });

  const requestPayload = {
    model: API_CONFIG.model,
    messages: [
      { role: "system", content: KNOWLEDGE_BASE_SYSTEM_PROMPT },
      ...chatHistory.slice(-8), // Ambil 8 percakapan terakhir agar konteks tetap terjaga
    ],
    temperature: 0.2, // Nilai rendah agar ketat pada basis pengetahuan model
    max_tokens: 600,
  };

  try {
    if (!API_CONFIG.apiKey || !API_CONFIG.apiKey.trim()) {
      throw new Error("API Key tidak diisi (beralih ke engine diagnostik basis pengetahuan lokal model).");
    }

    const response = await fetch(API_CONFIG.baseUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_CONFIG.apiKey.trim()}`,
      },
      body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error?.message || `HTTP ${response.status}`);
    }

    const data = await response.json();
    const replyText = data.choices?.[0]?.message?.content?.trim();

    if (!replyText) {
      throw new Error("Respon kosong dari penyedia model.");
    }

    // Format output teks ke HTML
    messageElement.innerHTML = replyText
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");

    // Simpan balasan ke histori
    chatHistory.push({
      role: "assistant",
      content: replyText,
    });
  } catch (error) {
    console.warn("Koneksi API gagal, beralih ke engine pengetahuan lokal:", error.message);
    // Jalankan engine diagnostik lokal berbasis aturan model
    const localReply = runLocalKnowledgeDiagnosis(userMessageText);
    messageElement.innerHTML = localReply
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");

    chatHistory.push({
      role: "assistant",
      content: localReply,
    });
  } finally {
    incomingMessageDiv.classList.remove("thinking");
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  }
};

// Penanganan pengiriman pesan
const handleOutgoingMessage = (e) => {
  if (e) e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  messageInput.value = "";
  messageInput.style.height = `${initialInputHeight}px`;

  // Tampilkan pesan pengguna
  const userDiv = createMessageElement(
    `<div class="message-text">${text}</div>`,
    "user-message"
  );
  chatBody.appendChild(userDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  setTimeout(() => {
    const botDivContent = `<img src="asset/logo-nst.jpeg" alt="NST" class="bot-avatar-img" /><div class="message-text">Sedang memeriksa basis pengetahuan model...</div>`;
    const incomingDiv = createMessageElement(botDivContent, "bot-message", "thinking");
    chatBody.appendChild(incomingDiv);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    generateBotResponse(incomingDiv, text);
  }, 250);
};

// Event Listeners
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleOutgoingMessage();
  }
});

messageInput.addEventListener("input", () => {
  messageInput.style.height = `${initialInputHeight}px`;
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
});

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e));

chatbotToggler.addEventListener("click", () => {
  document.body.classList.toggle("show-chatbot");
  if (document.body.classList.contains("show-chatbot")) {
    messageInput.focus();
  }
});

closeChatbot.addEventListener("click", () => {
  document.body.classList.remove("show-chatbot");
});

// Penanganan tombol trigger konsultasi di navbar dan hero section
document.querySelectorAll(".trigger-consultation").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.body.classList.add("show-chatbot");
    messageInput.focus();
  });
});

// Penanganan chip gejala cepat
document.querySelectorAll(".chip[data-symptom]").forEach((chip) => {
  chip.addEventListener("click", () => {
    const symptom = chip.getAttribute("data-symptom");
    if (!symptom) return;
    document.body.classList.add("show-chatbot");
    messageInput.value = symptom;
    handleOutgoingMessage();
  });
});
