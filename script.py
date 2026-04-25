import os
from pdfminer.high_level import extract_text

def main():
    pdf_folder = "pdfs"

    all_text = ""

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, file)

            print(f"Reading {file}...")

            try:
                text = extract_text(file_path)
                all_text += f"\n\n===== {file} =====\n\n"
                all_text += text
            except Exception as e:
                print(f"Error reading {file}: {e}")

    # 🔥 Save raw text
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(all_text)

    print("✅ test.txt created successfully!")

if __name__ == "__main__":
    main()
