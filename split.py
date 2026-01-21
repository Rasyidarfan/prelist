"""
Split PDF by "BLOK IV. CATATAN" marker
Each split file starts with a page containing "BLOK IV. CATATAN"
Files are named using QR code data from the next page
"""
import PyPDF2
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Clean text to make it a valid filename.
    Remove or replace invalid characters for Windows/Mac/Linux filenames.
    """
    # Remove or replace invalid characters
    # Invalid chars: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'

    # Replace invalid characters with underscore
    clean_text = re.sub(invalid_chars, '_', text)

    # Replace multiple spaces with single space
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Remove leading/trailing spaces and dots
    clean_text = clean_text.strip('. ')

    # Limit length
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length]

    # If empty after cleaning, use default
    if not clean_text:
        clean_text = "document"

    return clean_text

def extract_qr_data_from_text(text: str) -> str:
    """
    Extract and clean data that would be used for QR code.
    This should match the logic in the QR generation script.
    """
    # Try multiple possible keywords (same as QR generation)
    possible_keywords = [
        'Identitas Blok Sensus',
        'Identitas SLS',
        'IDENTITAS SAMPEL SATUAN LINGKUNGAN SETEMPAT',
        'IDENTITAS SAMPEL BLOK SENSUS',
        'Identitas',
    ]

    filtered_lines = []
    keyword_found = None
    text_lines = text.splitlines()

    # Try each keyword until we find matching lines
    for keyword in possible_keywords:
        temp_lines = []
        for line in text_lines:
            if keyword.lower() in line.lower():
                temp_lines.append(line)

        if temp_lines:
            filtered_lines = temp_lines
            keyword_found = keyword
            break

    # Process the text
    if filtered_lines:
        filtered_text = "\n".join(filtered_lines)
        # Remove all possible keywords
        for keyword in possible_keywords:
            filtered_text = filtered_text.replace(keyword, "")
    else:
        filtered_text = text

    # Clean the text (same as QR generation)
    filtered_text = ' '.join(filtered_text.split())

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

    # Remove extra spaces
    filtered_text = ' '.join(filtered_text.split()).strip()

    return filtered_text if filtered_text else "no_data"

def split_pdf_by_marker(pdf_path: str, output_folder: str, marker: str = "BLOK IV. CATATAN"):
    """
    Split PDF file into multiple files based on marker text.
    Each output file starts with a page containing the marker.
    """
    print(f"\n{'='*80}")
    print(f"PDF SPLITTER")
    print(f"{'='*80}")
    print(f"Input PDF: {pdf_path}")
    print(f"Output folder: {output_folder}")
    print(f"Marker: {marker}")
    print(f"{'='*80}\n")

    try:
        # Read the PDF
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)

            print(f"Total pages: {total_pages}\n")

            # Find all pages with the marker
            marker_pages = []
            page_texts = {}

            print("Scanning for markers...")
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                page_texts[page_num] = page_text

                if marker.lower() in page_text.lower():
                    marker_pages.append(page_num)
                    print(f"  ✓ Found '{marker}' on page {page_num + 1}")

            if not marker_pages:
                print(f"\n✗ No pages found with marker '{marker}'")
                messagebox.showwarning("No Markers Found",
                    f"No pages found containing '{marker}'.\nCannot split the PDF.")
                return

            print(f"\nFound {len(marker_pages)} marker(s)")
            print(f"Will create {len(marker_pages)} PDF file(s)\n")

            # Split the PDF
            created_files = []

            for i, start_page in enumerate(marker_pages):
                # Determine end page
                if i + 1 < len(marker_pages):
                    end_page = marker_pages[i + 1]
                else:
                    end_page = total_pages

                print(f"{'-'*80}")
                print(f"Processing split {i + 1}/{len(marker_pages)}")
                print(f"  Pages: {start_page + 1} to {end_page}")

                # Extract QR data from next page (if exists)
                qr_data = "no_data"
                if start_page + 1 < total_pages:
                    next_page_text = page_texts.get(start_page + 1, "")
                    if next_page_text:
                        qr_data = extract_qr_data_from_text(next_page_text)
                        print(f"  QR data extracted: {qr_data[:50]}{'...' if len(qr_data) > 50 else ''}")
                    else:
                        print(f"  Warning: Page {start_page + 2} has no text")
                else:
                    print(f"  Warning: No next page available for QR data")

                # Create filename
                base_filename = sanitize_filename(qr_data)
                filename = f"{base_filename}.pdf"

                # Handle duplicate filenames
                output_path = os.path.join(output_folder, filename)
                counter = 1
                while os.path.exists(output_path):
                    filename = f"{base_filename}_{counter}.pdf"
                    output_path = os.path.join(output_folder, filename)
                    counter += 1

                print(f"  Output: {filename}")

                # Create new PDF with pages from start_page to end_page
                writer = PyPDF2.PdfWriter()

                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])

                # Write to file
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

                created_files.append(filename)
                print(f"  ✓ Created successfully ({end_page - start_page} page(s))")

            print(f"\n{'='*80}")
            print(f"✓ SPLIT COMPLETE")
            print(f"{'='*80}")
            print(f"Total files created: {len(created_files)}")
            print(f"Output folder: {output_folder}")
            print(f"\nFiles created:")
            for i, filename in enumerate(created_files, 1):
                print(f"  {i}. {filename}")
            print(f"{'='*80}\n")

            messagebox.showinfo("Split Complete",
                f"Successfully split PDF into {len(created_files)} file(s).\n\n"
                f"Output folder:\n{output_folder}")

    except FileNotFoundError:
        print(f"✗ Error: File not found: {pdf_path}")
        messagebox.showerror("File Not Found", f"Cannot find file:\n{pdf_path}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

def select_pdf_file():
    """Open file dialog to select PDF file"""
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select PDF file to split",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    return file_path

def select_output_folder():
    """Open folder dialog to select output folder"""
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(
        title="Select folder to save split PDF files"
    )

    return folder_path

def main():
    """Main function"""
    print("\n" + "="*80)
    print("PDF SPLITTER - Split by 'BLOK IV. CATATAN'")
    print("="*80 + "\n")

    # Select input PDF
    print("Step 1: Select PDF file to split...")
    pdf_path = select_pdf_file()

    if not pdf_path:
        print("✗ No file selected. Exiting.")
        return

    print(f"✓ Selected: {pdf_path}\n")

    # Select output folder
    print("Step 2: Select output folder...")
    output_folder = select_output_folder()

    if not output_folder:
        print("✗ No folder selected. Exiting.")
        return

    print(f"✓ Selected: {output_folder}\n")

    # Confirm before proceeding
    response = messagebox.askyesno(
        "Confirm Split",
        f"Split this PDF?\n\n"
        f"Input: {os.path.basename(pdf_path)}\n"
        f"Output: {output_folder}\n\n"
        f"Files will be named based on QR code data."
    )

    if not response:
        print("✗ Cancelled by user.")
        return

    # Perform the split
    split_pdf_by_marker(pdf_path, output_folder)

if __name__ == "__main__":
    main()
