import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

def is_valid_roll(roll):
    return re.match(r'^1231\d+$', roll)

def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = text.split("\n")

    students = []
    current_student = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # =========================
        # 🎓 STUDENT DETECTION
        # =========================
        if re.match(r'^[A-Z ]+$', line) and len(line) > 3:
            if i + 1 < len(lines):
                roll = lines[i+1].strip()

                if is_valid_roll(roll):
                    current_student = {
                        "name": line,
                        "roll": roll,
                        "subjects": []
                    }
                    students.append(current_student)
                    i += 2
                    continue

        # =========================
        # 📘 SUBJECT DETECTION
        # =========================
        match = re.search(
            r'(\d+-\d+-\d+-\w+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+([PF])\s+([\d.]+)\s+([A-Z+]+)',
            line
        )

        if match and current_student:
            current_student["subjects"].append({
                "code": match.group(1),
                "name": match.group(2),
                "internal": int(match.group(3)),
                "external": int(match.group(4)),
                "credits": float(match.group(7))
            })

        i += 1

    return students


def main():
    all_students = {}

    for file in os.listdir("pdfs"):
        if file.endswith(".pdf"):
            semester = file.replace(".pdf", "")
            file_path = os.path.join("pdfs", file)

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

    print("✅ data.json generated")


if __name__ == "__main__":
    main()
