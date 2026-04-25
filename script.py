import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

def parse_pdf(file_path, semester):
    from pdfminer.high_level import extract_text
    import re

    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        # 🎓 Detect only 1231 roll
        if re.match(r'^1231\d{4}$', lines[i]):
            roll = lines[i]
            i += 1

            block = []

            # 📦 Collect full student block
            while i < len(lines) and not re.match(r'^1231\d{4}$', lines[i]):
                block.append(lines[i])
                i += 1

            # =========================
            # 🔍 Extract student name
            # =========================
            name = "UNKNOWN"
            for line in block:
                if re.match(r'^[A-Z ]+$', line) and len(line.split()) >= 2:
                    if "CGPA" not in line and "SGPA" not in line:
                        name = line
                        break

            # =========================
            # 🔍 Extract codes
            # =========================
            codes = [l for l in block if re.match(r'\d+-\d+-\d+-\w+', l)]

            # =========================
            # 🔍 Extract subject names
            # =========================
            subject_names = []
            for line in block:
                if re.match(r'^[A-Z ]+$', line) and len(line.split()) > 1:
                    if line != name:
                        subject_names.append(line)

            # =========================
            # 🔍 Extract numbers
            # =========================
            numbers = [int(l) for l in block if l.isdigit()]

            # split numbers into IM, EM, TOTAL
            n = len(codes)
            im = numbers[:n]
            em = numbers[n:2*n]
            total = numbers[2*n:3*n]

            # =========================
            # 🔍 Extract result
            # =========================
            results = [l for l in block if l in ["P", "F"]]

            # =========================
            # 🔗 Combine all
            # =========================
            subjects = []
            for idx in range(n):
                subjects.append({
                    "code": codes[idx],
                    "name": subject_names[idx] if idx < len(subject_names) else "",
                    "internal": im[idx] if idx < len(im) else 0,
                    "external": em[idx] if idx < len(em) else 0,
                    "total": total[idx] if idx < len(total) else 0,
                    "result": results[idx] if idx < len(results) else ""
                })

            students.append({
                "roll": roll,
                "name": name,
                "subjects": subjects
            })

        else:
            i += 1

    return students


def main():
    all_students = {}

    pdf_folder = "pdfs"

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            semester = file.replace(".pdf", "")
            file_path = os.path.join(pdf_folder, file)

            print(f"Processing {file}...")

            parsed = parse_pdf(file_path, semester)

            for student in parsed:
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

    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("✅ data.json generated successfully!")


if __name__ == "__main__":
    main()
