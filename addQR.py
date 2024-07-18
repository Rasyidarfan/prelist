import PyPDF2, qrcode, os, io, fitz
from PIL import Image
import tkinter as tk
from tkinter import filedialog

def extract_text_from_pdf(pdf_file: str) -> dict[int, str]:
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

def generate_qr_code_for_text(text: str, filename: str):
    qr = qrcode.QRCode(
        version=1,  # Adjust the version for desired QR code size
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    )

    filtered_text = text.strip().replace('\n', "")
    filtered_text = filtered_text.replace("SERUTI24.DSRT", "").replace("DAFTAR SAMPEL RUMAH TANGGA", "").replace("RAHASIA", "").replace("BLOK I. IDENTITAS SAMPEL BLOK SENSUS", "")
    filtered_text = filtered_text.replace("1. Provinsi", "").replace("2. Kabupaten/Kota", "").replace("3. Kecamatan", "").replace("4. Desa/Kelurahan", "").replace("5. Klasifikasi Desa/Kelurahan", "")
    filtered_text = filtered_text.replace("7. Nomor Kode Sampel (NKS)Perkotaan", "").replace("BLOK II. KETERANGAN PETUGAS", "").replace("Nama Pencacah", "").replace("PAPUA PEGUNUNGAN", "")
    filtered_text = filtered_text.replace("Pedesaan", "").replace("Nomor Blok Sensus", "").replace("Tgl. Pelaksanaan", "").replace("Tanda Tangan", "").replace("Nama Pengawas", "").replace("Tgl. Pelaksanaan", "")
    filtered_text = filtered_text.replace("Tanda Tangan", "").replace("BLOK III. CATATAN", "").replace("SURVEI EKONOMI RUMAH TANGGA TRIWULANAN 2024", "").replace("Triwulan 2", "")


    qr.add_data(filtered_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def embed_qr_codes_in_pdf(pdf_file: str, search_text: str, search_text_id: str, qr: object):
    page_text_dict = extract_text_from_pdf(pdf_file)

    pdf_doc = fitz.open(pdf_file)

    for page_num, page_text in page_text_dict.items():
        if search_text.lower() in page_text.lower():

            filtered_text = page_text_dict[page_num + 1].strip()  # Remove leading/trailing whitespace
            filtered_text_lines = filtered_text.splitlines()

            # Use a list comprehension to filter lines containing 'Identitas Blok Sensus'
            filtered_lines = []
            for line in filtered_text_lines:
                if search_text_id in line:
                    filtered_lines.append(line)

            filtered_text = "".join(filtered_lines).replace(search_text_id,"")
            qr_code_filename = f"qr_code_{page_num}.png"
            generate_qr_code_for_text(filtered_text, qr_code_filename)

            page = pdf_doc[page_num - 1] 
            qr_code_img = Image.open(qr_code_filename)

            # Convert image to bytes
            img_bytes = io.BytesIO()
            qr_code_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Insert image into PDF page
            image_rect = fitz.Rect(qr["x"], page.rect.height - qr["size"] - qr["y"], qr["x"] + qr["size"], page.rect.height - qr["y"])
            page.insert_image(image_rect, stream=img_bytes)

    pdf_doc.save(pdf_file.replace(".pdf","") + '_qr.pdf')

    # Remove generated QR code images (optional)
    for qr_code_filename in os.listdir():
        if qr_code_filename.startswith('qr_code_'):
            os.remove(qr_code_filename)

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf_file = file_path
        search_text_qr = 'BLOK IV. CATATAN'
        search_text_id = 'Identitas Blok Sensus'
        qr = {"size": 180, "x": 780, "y": 50}

        embed_qr_codes_in_pdf(pdf_file, search_text_qr, search_text_id, qr)
        print(f"QR codes embedded successfully")

if __name__ == "__main__":
    open_file_dialog()