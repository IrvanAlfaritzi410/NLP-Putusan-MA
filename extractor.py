# Library yang Dibutuhkan oleh Modul Ini 
import google.generativeai as genai
import json

# PROMPT UNIVERSAL 
# Prompt ini terisolasi di dalam modulnya sendiri.
PROMPT_UNIVERSAL = """
Anda adalah asisten hukum AI yang sangat ahli dalam menganalisis dan menstrukturkan dokumen putusan pengadilan di Indonesia.
Tugas Anda adalah membaca teks putusan berikut dan mengekstrak semua informasi yang relevan ke dalam format JSON yang telah ditentukan di bawah ini.

STRUKTUR JSON YANG WAJIB DIIKUTI:
{{
  "klasifikasi_perkara": "string (Pilih dari: Pidana Umum, Pidana Khusus, Pidana Militer, Perdata, Perdata Agama, Perdata Khusus, TUN, Pajak)",
  "informasi_umum": {{
    "nomor_putusan": "string",
    "nama_pengadilan": "string",
    "tingkat_pengadilan": "string (Contoh: Pengadilan Negeri, Pengadilan Tinggi, Mahkamah Agung)",
    "tanggal_putusan": "string (format: YYYY-MM-DD)"
  }},
  "para_pihak": [
    {{
      "peran_pihak": "string (Contoh: Terdakwa, Penggugat, Pemohon)",
      "nama_lengkap": "string",
      "tempat_lahir": "string",
      "tanggal_lahir": "string (format: YYYY-MM-DD)",
      "usia": "integer",
      "jenis_kelamin": "string",
      "pekerjaan": "string",
      "agama": "string",
      "alamat": "string",
      "nomor_ktp": "string",
      "nomor_kk": "string",
      "nomor_akta_kelahiran": "string",
      "nomor_paspor": "string"
    }}
  ],
  "detail_perkara": {{
    "riwayat_perkara": "string (rangkuman singkat 1-2 kalimat)",
    "dakwaan_jpu": "string (rangkuman dakwaan jika kasus pidana, null jika bukan)",
    "pokok_gugatan": "string (rangkuman gugatan jika kasus perdata/TUN, null jika bukan)",
    "riwayat_penahanan": "string (rangkuman riwayat penahanan jika ada, null jika tidak)"
  }},
  "amar_putusan": {{
    "amar_putusan_jpu": "string (rangkuman tuntutan jaksa jika ada, null jika tidak)",
    "amar_putusan_pn_pa_ptun": "string (rangkuman putusan tingkat pertama)",
    "amar_putusan_pt_pta_pttun": "string (rangkuman putusan tingkat banding, jika ada)",
    "amar_putusan_kasasi": "string (rangkuman putusan Mahkamah Agung/Kasasi ini)"
  }},
  "analisis_hukum": {{
    "pertimbangan_hukum": "string (rangkuman sangat singkat 2-3 kalimat mengenai dasar pertimbangan hakim)",
    "formalitas_permohonan": "string (rangkuman singkat info permohonan kasasi jika ada)"
  }}
}}

INSTRUKSI PENTING:
1.  `para_pihak`: Selalu dalam format LIST. Ekstrak SEMUA pihak yang terlibat.
2.  `RANGKUMAN`: Untuk semua field deskriptif, buatlah rangkuman inti sarinya saja.
3.  `NOMOR IDENTITAS`: Untuk `nomor_ktp`, dll., ekstrak HANYA ANGKA-nya saja.
4.  `null`: Jika informasi tidak ditemukan, WAJIB gunakan nilai null.

Sekarang, analisis teks putusan berikut dan buatlah JSON yang sesuai.
---
Teks Putusan: {teks_pdf}
---
"""

def ekstrak_data_dengan_gemini(model, teks_pdf):
    """
    Menganalisis teks PDF menggunakan model Gemini yang diberikan dan prompt universal.
    """
    if not model:
        print("  └─ ✗ Model Gemini tidak terkonfigurasi. Ekstraksi dibatalkan.")
        return None
        
    try:
        # Menggunakan prompt yang sudah didefinisikan di atas
        prompt = PROMPT_UNIVERSAL.format(teks_pdf=teks_pdf)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"  └─ ✗ Error saat memproses dengan Gemini: {e}")
        return None
