 #isi file cek_pdf.py

import fitz  # PyMuPDF
import os

# --- GANTI NAMA FILE DAN FOLDER DI BAWAH INI ---
NAMA_FOLDER_PDF = "putusan_ma" # Sesuaikan dengan nama folder Anda
NAMA_FILE_PDF = "putusan_22_pdt.p_2022_pn_sbr_20250722113631.pdf" # Ganti dengan nama file yang ingin dicek
# -----------------------------------------------

# Gabungkan path folder dan nama file
full_path = os.path.join(NAMA_FOLDER_PDF, NAMA_FILE_PDF)

try:
    print(f"Membaca teks dari file: {full_path}\n")
    
    # Buka file PDF dan ekstrak semua teksnya
    with fitz.open(full_path) as doc:
        raw_text = "".join(page.get_text() for page in doc)

    # Tampilkan teks mentah
    print("--- ISI TEKS MENTAH ---")
    print(raw_text)
    print("-------------------------")

except FileNotFoundError:
    print(f"✗ Error: File tidak ditemukan di '{full_path}'. Pastikan nama file dan folder sudah benar.")
except Exception as e:
    print(f"✗ Terjadi error saat membaca file: {e}")