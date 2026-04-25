import pdfplumber
import json
import re
import os

PREFIX = "1231"

def is_valid_roll(roll):
    return re.match(r'^1231\d+$', roll)

def parse_pdf(file_path, semester):
    students = []
    current_student = None
    last_subject = None

    with pdfplumber.open(file_path) as pdf:
        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # =========================
        # 🎓 STUDENT DETECTION
        # =========================
        if re.match(r'^[A-Z ]+$', line) and len(line) > 3:
            if i + 1 < len(lines):
                roll = lines[i+1].strip()

                if not is_valid_roll(roll):
                    i += 2
                    continue

                current_student = {
                    "name": line,
                    "roll": roll,
                    "semester": semester,
                    "subjects": []
                }

                students.append(current_student)
                i += 2
                continue

        # =========================
        # 📘 SUBJECT DETECTION
        # =========================
        subject_match = re.match(
            r'(\d+-\d+-\d+-\w+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+([PF])\s+([\d.]+)\s+([A-Z+]+)',
            line
        )

        if subject_match and current_student:
            code = subject_match.group(1)
            name = subject_match.group(2)
            internal = int(subject_match.group(3))
            external = int(subject_match.group(4))
            total = int(subject_match.group(5))
            result = subject_match.group(6)
            credits = float(subject_match.group(7))

            sub = {
                "code": code,
                "name": name,
                "internal": internal,
                "external": external,
                "credits": credits
            }

            current_student["subjects"].append(sub)
            last_subject = sub

        else:
            # =========================
            # 🔗 MULTI-LINE SUBJECT FIX
            # =========================
            if current_student and last_subject:
                # If line doesn't look like marks, append to subject name
                if not re.search(r'\d+\s+\d+\s+\d+', line):
                    last_subject["name"] += " " + line

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

            parsed_students = parse_pdf(file_path, semester)

            for student in parsed_students:
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

    output = {
        "students": list(all_students.values())
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✅ data.json generated successfully!")


if __name__ == "__main__":
    main()
