import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

# ❌ Words to ignore as fake names
INVALID_NAMES = ["GRADE", "SUBCODE", "RESULT", "TOTAL", "CREDITS"]

def is_valid_roll(roll):
    return re.match(r'^1231\d+$', roll)

def is_valid_name(name):
    if name in INVALID_NAMES:
        return False
    if len(name.split()) < 2:
        return False
    return True


def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    current_student = None

    subject_pattern = re.compile(
        r'(\d+-\d+-\d+-\w+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+([PF])\s+([\d.]+)\s+([A-Z+]+)'
    )

    i = 0
    while i < len(lines):
        line = lines[i]

        # =========================
        # 🎓 CASE 1: NAME + ROLL SAME LINE
        # =========================
        match = re.match(r'^([A-Z ]+)\s+(1231\d+)$', line)
        if match and is_valid_name(match.group(1)):
            current_student = {
                "name": match.group(1).strip(),
                "roll": match.group(2),
                "subjects": []
            }
            students.append(current_student)
            i += 1
            continue

        # =========================
        # 🎓 CASE 2: NAME + NEXT LINE ROLL
        # =========================
        if re.match(r'^[A-Z ]+$', line) and is_valid_name(line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                if is_valid_roll(next_line):
                    current_student = {
                        "name": line,
                        "roll": next_line,
                        "subjects": []
                    }
                    students.append(current_student)
                    i += 2
                    continue

        # =========================
        # 📘 SUBJECT DETECTION
        # =========================
        if current_student:
            match = subject_pattern.search(line)

            if match:
                current_student["subjects"].append({
                    "code": match.group(1),
                    "name": match.group(2),
                    "internal": int(match.group(3)),
                    "external": int(match.group(4)),
                    "credits": float(match.group(7))
                })
            else:
                # 🔗 Handle multi-line subject names
                if i + 1 < len(lines):
                    combined = line + " " + lines[i + 1]
                    match = subject_pattern.search(combined)

                    if match:
                        current_student["subjects"].append({
                            "code": match.group(1),
                            "name": match.group(2),
                            "internal": int(match.group(3)),
                            "external": int(match.group(4)),
                            "credits": float(match.group(7))
                        })
                        i += 1  # skip next line since used

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
