"""
Flexible QR Code Generator for PDF Forms
Supports multiple form types with different identifiers
"""
import PyPDF2, qrcode, os, io, fitz, re
from PIL import Image
import tkinter as tk
from tkinter import filedialog

def extract_text_from_pdf(pdf_file: str) -> dict[int, str]:
    """Extract text from all pages of a PDF file"""
    page_text_dict = {}

    try:
        with open(pdf_file, 'rb') as pdf:
            reader = PyPDF2.PdfReader(pdf)

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                page_text_dict[page_num + 1] = page_text

    except FileNotFoundError:
        print(f"Error: File '{pdf_file}' not found.")
    except PyPDF2.errors.PdfReadError:
        print(f"Error: Unable to read PDF file '{pdf_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return page_text_dict

def extract_identity_data(text: str) -> str:
    """
    Extract identity/location data from text using flexible pattern matching.
    Works with various form layouts.
    """
    # Try to find lines starting with numbers (like "1. Provinsi", "2. Kabupaten")
    identity_lines = []
    lines = text.splitlines()

    for line in lines:
        # Match lines that start with digits followed by dot (1., 2., 3., etc.)
        if re.match(r'^\d+\.', line.strip()):
            identity_lines.append(line)

    if identity_lines:
        result = '\n'.join(identity_lines)
    else:
        # Fallback: use the entire text
        result = text

    return result

def generate_qr_code_for_text(text: str, filename: str):
    """Generate QR code from text with extensive cleaning and logging"""
    qr = qrcode.QRCode(
        version=None,  # Auto-adjust version based on data size
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (30%)
        box_size=10,
        border=4,
    )

    # LOG: Original text
    print(f"\n  [LOG] ORIGINAL TEXT (length={len(text)}):")
    print(f"  {'-'*70}")
    print(f"  {text[:200]}")
    if len(text) > 200:
        print(f"  ... (truncated, total {len(text)} chars)")
    print(f"  {'-'*70}")

    # Clean the text more thoroughly
    filtered_text = text.strip()

    # Remove all newlines and extra spaces
    filtered_text = ' '.join(filtered_text.split())

    # LOG: After normalizing spaces
    print(f"\n  [LOG] AFTER NORMALIZING SPACES (length={len(filtered_text)}):")
    print(f"  {'-'*70}")
    print(f"  {filtered_text[:200]}")
    if len(filtered_text) > 200:
        print(f"  ... (truncated, total {len(filtered_text)} chars)")
    print(f"  {'-'*70}")

    # Remove common headers and labels
    remove_strings = [
        "SERUTI24.DSRT", "DAFTAR SAMPEL RUMAH TANGGA", "RAHASIA",
        "BLOK I. IDENTITAS SAMPEL BLOK SENSUS", "1. Provinsi",
        "2. Kabupaten/Kota", "3. Kecamatan", "4. Desa/Kelurahan",
        "5. Klasifikasi Desa/Kelurahan", "7. Nomor Kode Sampel (NKS)Perkotaan",
        "BLOK II. KETERANGAN PETUGAS", "Nama Pencacah",
        "Pedesaan", "Perkotaan", "Nomor Blok Sensus", "Tgl. Pelaksanaan",
        "Tanda Tangan", "Nama Pengawas", "BLOK III. CATATAN",
        "SURVEI EKONOMI RUMAH TANGGA TRIWULANAN 2024", "Triwulan 2",
        "BLOK I. IDENTITAS SAMPEL SATUAN LINGKUNGAN SETEMPAT",
        "6. Kode SLS/Sub-SLS", "8. Satuan Lingkungan Setempat (SLS)",
        "BLOK II. REKAPITULASI HASIL PEMUTAKHIRAN",
        "BLOK III. KETERANGAN PETUGAS", "BLOK IV. CATATAN",
        "Identitas Blok Sensus", "Identitas SLS",
        "SURVEI SOSIAL EKONOMI NASIONAL 2020",
        "DAFTAR PEMUTAKHIRAN RUMAH TANGGA", "Sumber Data : DTSEN",
        "SAMPEL SERUTI", "BLOK I.", "BLOK II.", "BLOK III.", "BLOK IV.",
        "Kabupaten/Kota *)", "Desa/Kelurahan *)", "*) Coret yang tidak perlu"
    ]

    for s in remove_strings:
        filtered_text = filtered_text.replace(s, "")

    # Remove extra spaces again after replacements
    filtered_text = ' '.join(filtered_text.split()).strip()

    # LOG: After filtering
    print(f"\n  [LOG] AFTER FILTERING (length={len(filtered_text)}):")
    print(f"  {'-'*70}")
    if filtered_text:
        print(f"  {filtered_text}")
    else:
        print(f"  <EMPTY - NO DATA LEFT>")
    print(f"  {'-'*70}")

    # Ensure we have data to encode
    if not filtered_text:
        print(f"\n  [WARNING] No data after filtering! Using 'NO_DATA'")
        filtered_text = "NO_DATA"

    # LOG: Final data to encode
    print(f"\n  [LOG] FINAL DATA TO ENCODE IN QR:")
    print(f"  {'-'*70}")
    print(f"  {filtered_text}")
    print(f"  {'-'*70}")
    print(f"  Length: {len(filtered_text)} characters")

    qr.add_data(filtered_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

    print(f"  QR Code Version: {qr.version}")

def embed_qr_codes_in_pdf(pdf_file: str, search_text: str, search_text_id: str, qr: object):
    """
    Embed QR codes in PDF with flexible keyword matching.
    Searches for multiple possible identifiers in the next page.
    """
    page_text_dict = extract_text_from_pdf(pdf_file)

    pdf_doc = fitz.open(pdf_file)
    qr_count = 0

    for page_num, page_text in page_text_dict.items():
        if search_text.lower() in page_text.lower():

            print(f"\n{'='*80}")
            print(f"PROCESSING PAGE {page_num}")
            print(f"{'='*80}")

            # Check if next page exists
            if page_num + 1 not in page_text_dict:
                print(f"[WARNING] Page {page_num + 1} does not exist, skipping...")
                continue

            filtered_text = page_text_dict[page_num + 1].strip()

            print(f"\n[STEP 1] Full text from page {page_num + 1} (length={len(filtered_text)}):")
            print(f"{'-'*70}")
            print(f"{filtered_text[:300]}")
            if len(filtered_text) > 300:
                print(f"... (truncated, total {len(filtered_text)} chars)")
            print(f"{'-'*70}")

            # Try multiple possible keywords (FLEXIBLE SEARCH)
            possible_keywords = [
                'Identitas Blok Sensus',
                'Identitas SLS',
                'IDENTITAS SAMPEL SATUAN LINGKUNGAN SETEMPAT',
                'IDENTITAS SAMPEL BLOK SENSUS',
                'Identitas',
            ]

            filtered_lines = []
            keyword_found = None
            filtered_text_lines = filtered_text.splitlines()

            # Try each keyword until we find matching lines
            for keyword in possible_keywords:
                temp_lines = []
                for line in filtered_text_lines:
                    if keyword.lower() in line.lower():  # Case-insensitive search
                        temp_lines.append(line)

                if temp_lines:
                    filtered_lines = temp_lines
                    keyword_found = keyword
                    break

            print(f"\n[STEP 2] Keyword search result:")
            print(f"{'-'*70}")
            if keyword_found:
                print(f"✓ Found keyword: '{keyword_found}'")
                print(f"  Matched lines: {len(filtered_lines)}")
                for i, line in enumerate(filtered_lines[:5], 1):  # Show first 5
                    print(f"  {i}. {line}")
                if len(filtered_lines) > 5:
                    print(f"  ... and {len(filtered_lines) - 5} more lines")
            else:
                print(f"✗ No specific keyword found")
                print(f"  Using entire page text")
                filtered_lines = []
            print(f"{'-'*70}")

            # Process the text
            if filtered_lines:
                # Use only the matched lines
                filtered_text = "\n".join(filtered_lines)
                # Remove all possible keywords
                for keyword in possible_keywords:
                    filtered_text = filtered_text.replace(keyword, "")
            # else: keep the entire page text

            print(f"\n[STEP 3] Text to be encoded:")
            print(f"{'-'*70}")
            print(f"Length: {len(filtered_text)}")
            print(f"Preview: {filtered_text[:200] if filtered_text else '<EMPTY>'}")
            print(f"{'-'*70}")

            qr_code_filename = f"qr_code_{page_num}.png"
            generate_qr_code_for_text(filtered_text, qr_code_filename)

            print(f"\n[SUCCESS] QR code generated: {qr_code_filename}\n")

            page = pdf_doc[page_num - 1]
            qr_code_img = Image.open(qr_code_filename)

            # Convert image to bytes
            img_bytes = io.BytesIO()
            qr_code_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Insert image into PDF page
            image_rect = fitz.Rect(qr["x"], page.rect.height - qr["size"] - qr["y"], qr["x"] + qr["size"], page.rect.height - qr["y"])
            page.insert_image(image_rect, stream=img_bytes)

            qr_count += 1

    output_file = pdf_file.replace(".pdf","") + '_qr.pdf'
    pdf_doc.save(output_file)

    print(f"\n{'='*80}")
    print(f"✓ Successfully embedded {qr_count} QR code(s)")
    print(f"✓ Output file: {output_file}")
    print(f"{'='*80}\n")

    # Remove generated QR code images (optional)
    for qr_code_filename in os.listdir():
        if qr_code_filename.startswith('qr_code_'):
            os.remove(qr_code_filename)

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        print(f"\n{'='*80}")
        print(f"Flexible QR Code Generator")
        print(f"Processing: {file_path}")
        print(f"{'='*80}\n")

        pdf_file = file_path
        search_text_qr = 'BLOK IV. CATATAN'
        search_text_id = None  # Not used anymore - flexible search
        qr = {"size": 180, "x": 780, "y": 50}

        embed_qr_codes_in_pdf(pdf_file, search_text_qr, search_text_id, qr)
    else:
        print("No file selected.")

if __name__ == "__main__":
    open_file_dialog()
