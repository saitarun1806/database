import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

def is_valid_roll(roll):
    return re.match(r'^1231\d+$', roll)

def parse_pdf(file_path, semester):
    from pdfminer.high_level import extract_text
    import re

    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    current_student = None

    for i, line in enumerate(lines):

        # =========================
        # 🎓 CASE 1: NAME + ROLL SAME LINE
        # =========================
        match = re.match(r'^([A-Z ]+)\s+(1231\d+)$', line)
        if match:
            current_student = {
                "name": match.group(1).strip(),
                "roll": match.group(2),
                "subjects": []
            }
            students.append(current_student)
            continue

        # =========================
        # 🎓 CASE 2: NAME + NEXT LINE ROLL
        # =========================
        if re.match(r'^[A-Z ]+$', line):
            if i + 1 < len(lines):
                next_line = lines[i+1]

                if re.match(r'^1231\d+$', next_line):
                    current_student = {
                        "name": line,
                        "roll": next_line,
                        "subjects": []
                    }
                    students.append(current_student)
                    continue

        # =========================
        # 📘 SUBJECT DETECTION
        # =========================
        subject_match = re.search(
            r'(\d+-\d+-\d+-\w+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+([PF])\s+([\d.]+)\s+([A-Z+]+)',
            line
        )

        if subject_match and current_student:
            current_student["subjects"].append({
                "code": subject_match.group(1),
                "name": subject_match.group(2),
                "internal": int(subject_match.group(3)),
                "external": int(subject_match.group(4)),
                "credits": float(subject_match.group(7))
            })

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
