# Library Standar Python 
import os
import json
import time

# Library Pihak Ketiga
import google.generativeai as genai

# MENGHUBUNGKAN SEMUA MODUL 
# 1. Impor semua variabel konfigurasi dari file config.py
import config 

# 2. Impor fungsi utama dari file Proses_URL.py
from proses_URL import proses_putusan_from_url 

# Fungsi Setup Model 
def setup_model():
    """Mengkonfigurasi dan mengembalikan model Gemini menggunakan variabel dari config."""
    # Menggunakan GOOGLE_API_KEY dari config.py
    if config.GOOGLE_API_KEY:
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            # Menggunakan MODEL_NAME dari config.py
            model = genai.GenerativeModel(config.MODEL_NAME)
            print("✓ Konfigurasi Gemini API berhasil.")
            return model
        except Exception as e:
            print(f"✗ Konfigurasi API gagal: {e}")
            return None
    else:
        print("✗ Kunci API tidak tersedia di config.py atau .env file.")
        return None

# Fungsi Utama untuk Menjalankan Seluruh Proses 
def main():
    model = setup_model()
    if not model:
        print("Eksekusi dihentikan karena konfigurasi model gagal.")
        return
    
    # Membuat folder untuk unduhan jika belum ada (menggunakan variabel dari config)
    if not os.path.exists(config.PDF_DOWNLOAD_FOLDER):
        os.makedirs(config.PDF_DOWNLOAD_FOLDER)
        print(f"✓ Folder '{config.PDF_DOWNLOAD_FOLDER}' berhasil dibuat.")

    list_url_putusan = [
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/42dfaa53298aa3a2649588946b89167e.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf066d7f7faca26a8ec313534333431.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/84771ffa631520272cab7efbc09042c0.html"
    ]
    
    list_hasil_akhir = []
    if os.path.exists(config.OUTPUT_FILENAME_JSON):
        try:
            with open(config.OUTPUT_FILENAME_JSON, 'r', encoding='utf-8') as f:
                list_hasil_akhir = json.load(f)
        except json.JSONDecodeError:
            pass
    
    processed_urls = {item.get('sumber_url') for item in list_hasil_akhir}
    urls_to_process = [url for url in list_url_putusan if url not in processed_urls]

    if not urls_to_process:
        print("\n✓ Semua URL sudah diproses sebelumnya.")
    else:
        print(f"\nMenemukan {len(urls_to_process)} URL baru untuk diproses.")
        for i, url in enumerate(urls_to_process):
            # PERBAIKAN PENTING: Meneruskan objek 'model' ke dalam fungsi
            hasil = proses_putusan_from_url(model, url)
            if hasil:
                list_hasil_akhir.append(hasil)
                print("  └─ ✓ Ekstraksi dari URL berhasil!\n")
            else:
                print("  └─ ✗ Gagal memproses URL ini.\n")
            
            # Jeda antar file untuk menghindari limit API
            if i < len(urls_to_process) - 1:
                time.sleep(20)

    if list_hasil_akhir:
        print(f"\nMenyimpan total {len(list_hasil_akhir)} data ke dalam file JSON...")
        # Menggunakan nama file output dari config.py
        with open(config.OUTPUT_FILENAME_JSON, 'w', encoding='utf-8') as f:
            json.dump(list_hasil_akhir, f, ensure_ascii=False, indent=4)
        print(f"✓ Data berhasil disimpan di '{config.OUTPUT_FILENAME_JSON}'")
    else:
        print("\nTidak ada data yang berhasil diekstrak.")

# --- Titik Masuk Eksekusi Skrip ---
if __name__ == "__main__":
    main()
