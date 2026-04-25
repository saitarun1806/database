import os
from pdfminer.high_level import extract_text

def main():
    pdf_folder = "pdfs"

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, file)

            print("\n==============================")
            print(f"FILE: {file}")
            print("==============================\n")

            try:
                text = extract_text(file_path)

                # 🔥 Print only first part (avoid huge logs)
                print(text[:2000])  

            except Exception as e:
                print(f"Error reading {file}: {e}")

if __name__ == "__main__":
    main()
