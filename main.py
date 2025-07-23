#Fungsi Utama untuk Menjalankan Seluruh Proses
def main():
    if not model:
        print("Eksekusi dihentikan karena konfigurasi model gagal.")
        return
    
    # PERUBAHAN: Membuat folder untuk unduhan jika belum ada
    if not os.path.exists(PDF_DOWNLOAD_FOLDER):
        os.makedirs(PDF_DOWNLOAD_FOLDER)
        print(f"✓ Folder '{PDF_DOWNLOAD_FOLDER}' berhasil dibuat.")

    list_url_putusan = [
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/42dfaa53298aa3a2649588946b89167e.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf066d7f7faca26a8ec313534333431.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/84771ffa631520272cab7efbc09042c0.html"
    ]
    
    list_hasil_akhir = []
    if os.path.exists(OUTPUT_FILENAME_JSON):
        try:
            with open(OUTPUT_FILENAME_JSON, 'r', encoding='utf-8') as f:
                list_hasil_akhir = json.load(f)
        except json.JSONDecodeError:
            pass
    
    processed_urls = {item.get('sumber_url') for item in list_hasil_akhir}
    urls_to_process = [url for url in list_url_putusan if url not in processed_urls]

    if not urls_to_process:
        print("\n✓ Semua URL sudah diproses sebelumnya.")
    else:
        print(f"\nMenemukan {len(urls_to_process)} URL baru untuk diproses.")
        for url in urls_to_process:
            hasil = proses_putusan_from_url(url)
            if hasil:
                list_hasil_akhir.append(hasil)
                print("  └─ ✓ Ekstraksi dari URL berhasil!\n")
            else:
                print("  └─ ✗ Gagal memproses URL ini.\n")
            
            time.sleep(20)

    if list_hasil_akhir:
        print(f"\nMenyimpan total {len(list_hasil_akhir)} data ke dalam file JSON...")
        with open(OUTPUT_FILENAME_JSON, 'w', encoding='utf-8') as f:
            json.dump(list_hasil_akhir, f, ensure_ascii=False, indent=4)
        print(f"✓ Data berhasil disimpan di '{OUTPUT_FILENAME_JSON}'")
    else:
        print("\nTidak ada data yang berhasil diekstrak.")

if __name__ == "__main__":
    main()
