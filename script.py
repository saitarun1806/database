import json
import re
import os
from pdfminer.high_level import extract_text

def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # =========================
        # 🎓 DETECT ROLL NUMBER
        # =========================
        if re.match(r'^1231\d+$', line):
            roll = line
            subjects = []
            i += 1

            # =========================
            # 📘 READ SUBJECTS UNTIL **********
            # =========================
            while i < len(lines) and "**********" not in lines[i]:
                sub_line = lines[i]

                match = re.match(
                    r'(\d+-\d+-\d+-\w+)\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+([PF])\s+([\d.]+)\s+([A-Z+]+)',
                    sub_line
                )

                if match:
                    subjects.append({
                        "code": match.group(1),
                        "name": match.group(2),
                        "internal": int(match.group(3)),
                        "external": int(match.group(4)),
                        "credits": float(match.group(7))
                    })

                i += 1

            # =========================
            # ⏭️ SKIP ********** + TOTAL LINE
            # =========================
            while i < len(lines) and not re.match(r'^[A-Z ]+$', lines[i]):
                i += 1

            # =========================
            # 🧑‍🎓 GET NAME (AFTER TOTAL)
            # =========================
            name = "UNKNOWN"

            if i < len(lines):
                name_line = lines[i]

                if re.match(r'^[A-Z ]+$', name_line) and len(name_line.split()) >= 2:
                    name = name_line

            # =========================
            # ✅ SAVE STUDENT
            # =========================
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

    print("✅ data.json generated successfully!")


if __name__ == "__main__":
    main()
