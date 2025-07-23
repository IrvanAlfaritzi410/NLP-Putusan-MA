#A. Import library
import os
import json
import pandas as pd
import fitz  # PyMuPDF
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

load_dotenv()

 #B. Konfigurasi Proyek
PDF_DOWNLOAD_FOLDER = 'downloaded_pdfs'
OUTPUT_FILENAME_JSON = 'hasil_ekstraksi_putusan.json'
MODEL_NAME = 'gemini-2.5-flash'

 #C. Setup API Key Gemini
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
