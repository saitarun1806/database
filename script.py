import pdfplumber
import json
import re
import os

# Accept both roll types
def is_valid_roll(line):
    return re.match(r'^1231[67]\d+', line)


# =========================
# 🔹 Extract text
# =========================
def extract_text_from_pdf(pdf_path):
    text_data = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_data += "\n" + text

    return text_data


# =========================
# 🔹 Parse text
# =========================
def parse_text(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        if is_valid_roll(lines[i]):

            parts = lines[i].split(" ", 1)
            roll = parts[0]
            name = parts[1] if len(parts) > 1 else "UNKNOWN"

            i += 1
            subjects = []

            while i < len(lines):

                line = lines[i]

                if is_valid_roll(line):
                    break

                if "CGPA" in line:
                    i += 1
                    break

                if re.match(r'\d+-\d+-\d+-', line):

                    parts = line.split()

                    try:
                        code = parts[0]
                        internal = parts[-6]
                        external = parts[-5]
                        total = parts[-4]
                        result = parts[-3]

                        subject_name = " ".join(parts[1:-6])

                        if result == "AL":
                            result = "F"

                        subjects.append({
                            "code": code,
                            "name": subject_name,
                            "internal": internal,
                            "external": external,
                            "total": total,
                            "result": result
                        })

                    except:
                        pass

                i += 1

            students.append({
                "roll": roll,
                "name": name,
                "subjects": subjects
            })

        else:
            i += 1

    return students


# =========================
# 🔹 MAIN
# =========================
def main():
    pdf_folder = "pdfs"
    all_students = {}

    for root, dirs, files in os.walk(pdf_folder):
        for file in files:
            if file.endswith(".pdf"):

                file_path = os.path.join(root, file)

                # ✅ Keep semester SAME (sem1, sem2)
                semester = file.replace(".pdf", "")

                print(f"Processing {file_path}...")

                text = extract_text_from_pdf(file_path)
                students = parse_text(text)

                for student in students:
                    roll = student["roll"]

                    if roll not in all_students:
                        all_students[roll] = {
                            "roll": roll,
                            "name": student["name"],
                            "semesters": {}
                        }

                    all_students[roll]["semesters"][semester] = {
                        "subjects": student["subjects"]
                    }

    # Save JSON
    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("🎉 Done! Both AI & Regular merged correctly.")


if __name__ == "__main__":
    main()
