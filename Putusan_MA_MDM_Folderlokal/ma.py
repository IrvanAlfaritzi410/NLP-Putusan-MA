# ==============================================================================
# SCRIPT PIPELINE LENGKAP - EKSTRAKSI DARI FOLDER LOKAL (PROMPT UNIVERSAL)
# ==============================================================================

# --- 1. Impor Library ---
import os
import json
import fitz  # PyMuPDF
import google.generativeai as genai
import time
from dotenv import load_dotenv

# Muat environment variable dari file .env (jika ada)
load_dotenv()

# --- 2. Konfigurasi Proyek ---
FOLDER_PATH = 'putusan_ma'  # NAMA FOLDER TEMPAT ANDA MENYIMPAN PDF
OUTPUT_FILENAME_JSON = 'hasil_ekstraksi_putusan.json'
MODEL_NAME = 'gemini-1.5-flash-latest'

# --- 3. Setup API Key Gemini ---
GOOGLE_API_KEY = os.environ.get('GEMINI_API_KEY')
model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        print("✓ Konfigurasi Gemini API berhasil.")
    except Exception as e:
        print(f"✗ Konfigurasi API gagal: {e}")
else:
    print("✗ Peringatan: Environment variable 'GEMINI_API_KEY' tidak ditemukan.")

# --- 4. Fungsi Ekstraksi Data Universal (PROMPT BARU) ---
def ekstrak_data_dengan_gemini(teks_pdf):
    """
    Menganalisis teks PDF dan mengekstrak informasi detail.
    Jika ada beberapa pihak, fungsi ini akan mengembalikan LIST of JSON objects.
    """
    # PROMPT BARU: Menggunakan satu struktur universal dengan tipe data generik.
    prompt = f"""
    Anda adalah asisten hukum AI yang sangat ahli dalam menganalisis dan menstrukturkan dokumen putusan pengadilan di Indonesia.
    Tugas Anda adalah membaca teks putusan berikut dan mengekstrak semua informasi yang relevan ke dalam format JSON yang telah ditentukan di bawah ini.

    STRUKTUR OUTPUT:
    - Jika hanya ada SATU pihak utama (misal: satu terdakwa), kembalikan satu objek JSON.
    - Jika ada LEBIH DARI SATU pihak utama (misal: Terdakwa 1 & Terdakwa 2), kembalikan LIST yang berisi beberapa objek JSON, satu untuk setiap pihak. Setiap objek dalam list harus berisi semua informasi perkara yang sama, hanya data identitas pihak yang berbeda.

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
    1.  `para_pihak`: Selalu dalam format LIST. Ekstrak SEMUA pihak yang terlibat. Untuk setiap pihak, buatkan objek JSON terpisah.
    2.  `RANGKUMAN`: Untuk semua field deskriptif, buatlah rangkuman inti sarinya saja dalam 1-3 kalimat.
    3.  `NOMOR IDENTITAS`: Untuk `nomor_ktp`, `nomor_kk`, dll., ekstrak HANYA ANGKA-nya saja sebagai string.
    4.  `null`: Jika ada informasi yang tidak ditemukan, WAJIB gunakan nilai null.

    Sekarang, analisis teks putusan berikut dan buatlah JSON yang sesuai.
    ---
    Teks Putusan: {teks_pdf}
    ---
    """
    if not model:
        return None
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"  └─ ✗ Error saat memproses dengan Gemini: {e}")
        return None

# --- 5. Fungsi Utama untuk Menjalankan Seluruh Proses ---
def main():
    if not model:
        print("Eksekusi dihentikan karena konfigurasi model gagal.")
        return

    # Memuat data lama dari file JSON
    list_hasil_akhir = []
    if os.path.exists(OUTPUT_FILENAME_JSON):
        try:
            with open(OUTPUT_FILENAME_JSON, 'r', encoding='utf-8') as f:
                list_hasil_akhir = json.load(f)
            print(f"✓ Ditemukan {len(list_hasil_akhir)} data yang sudah diproses sebelumnya.")
        except json.JSONDecodeError:
            print(f"i Info: File '{OUTPUT_FILENAME_JSON}' ditemukan tapi kosong. Memulai dari awal.")
        except Exception as e:
            print(f"✗ Error saat membaca file JSON yang ada: {e}")
    
    processed_files = {item.get('nama_file') for item in list_hasil_akhir}
    
    # Menyiapkan daftar file PDF baru untuk diproses dari folder lokal
    if not os.path.isdir(FOLDER_PATH):
        print(f"✗ Error: Folder '{FOLDER_PATH}' tidak ditemukan.")
        return
        
    files_to_process = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith('.pdf') and f not in processed_files]

    if not files_to_process:
        print("\n✓ Semua file PDF di folder sudah diproses.")
    else:
        print(f"\nMenemukan {len(files_to_process)} file baru untuk diproses.")
        for i, filename in enumerate(files_to_process):
            full_path = os.path.join(FOLDER_PATH, filename)
            print(f"[{i+1}/{len(files_to_process)}] Memproses file: {filename}...")
            
            try:
                with fitz.open(full_path) as doc:
                    full_text = "".join(page.get_text() for page in doc)

                if full_text.strip():
                    hasil_json = ekstrak_data_dengan_gemini(full_text)
                    
                    if hasil_json:
                        # LOGIKA BARU: Menangani output yang bisa berupa dict atau list of dict
                        if isinstance(hasil_json, list):
                            # Jika hasilnya list (banyak pihak), tambahkan nama file ke setiap item
                            for item in hasil_json:
                                item['nama_file'] = filename
                            list_hasil_akhir.extend(hasil_json)
                        elif isinstance(hasil_json, dict):
                            # Jika hasilnya dict (satu pihak), tambahkan nama file
                            hasil_json['nama_file'] = filename
                            list_hasil_akhir.append(hasil_json)
                        
                        print("  └─ ✓ Data berhasil diekstrak.\n")
                    else:
                        print("  └─ ✗ Gagal mengekstrak data dari file ini.\n")
                
                # Jeda antar file untuk menghindari limit API
                if i < len(files_to_process) - 1:
                    time.sleep(20)

            except Exception as e:
                print(f"  └─ ✗ Gagal memproses file {filename}: {e}\n")

    # Menyimpan hasil akhir ke file JSON
    if list_hasil_akhir:
        print(f"\nMenyimpan total {len(list_hasil_akhir)} data ke dalam file JSON...")
        with open(OUTPUT_FILENAME_JSON, 'w', encoding='utf-8') as f:
            json.dump(list_hasil_akhir, f, ensure_ascii=False, indent=4)
        print(f"✓ Data berhasil disimpan di '{OUTPUT_FILENAME_JSON}'")
    else:
        print("\nTidak ada data baru untuk diproses atau disimpan.")

# --- Titik Masuk Eksekusi Skrip ---
if __name__ == "__main__":
    main()
