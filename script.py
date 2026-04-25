import os
from pdfminer.high_level import extract_text

def main():
    pdf_folder = "pdfs"

    with open("test.txt", "w", encoding="utf-8") as f:

        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                file_path = os.path.join(pdf_folder, file)

                print(f"Reading {file}...")

                try:
                    text = extract_text(file_path)

                    f.write("\n\n==============================\n")
                    f.write(f"FILE: {file}\n")
                    f.write("==============================\n\n")

                    f.write(text)

                except Exception as e:
                    f.write(f"\nError reading {file}: {e}\n")

    print("✅ test.txt created successfully!")

if __name__ == "__main__":
    main()
