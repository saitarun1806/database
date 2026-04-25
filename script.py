import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # =========================
        # 🎓 DETECT ONLY 1231 ROLL
        # =========================
        if line.startswith(PREFIX) and line.isdigit() and len(line) == 8:
            roll = line
            i += 1

            codes = []
            names = []
            im = []
            em = []
            total = []
            result = []

            student_name = "UNKNOWN"

            # =========================
            # 📘 READ STUDENT BLOCK
            # =========================
            while i < len(lines) and not (lines[i].startswith(PREFIX) and lines[i].isdigit()):
                current = lines[i]

                # subject codes
                if re.match(r'\d+-\d+-\d+-\w+', current):
                    codes.append(current)

                # detect student name (long uppercase)
                elif re.match(r'^[A-Z ]+$', current) and len(current.split()) >= 2:
                    # ignore headers
                    if current not in ["SUBCODE", "SUBNAME", "GRADE", "RESULT"]:
                        student_name = current

                # subject names
                elif re.match(r'^[A-Z ]+$', current):
                    names.append(current)

                # numeric values
                elif current.isdigit():
                    num = int(current)

                    if len(im) < len(codes):
                        im.append(num)
                    elif len(em) < len(codes):
                        em.append(num)
                    else:
                        total.append(num)

                # result values
                elif current in ["P", "F"]:
                    result.append(current)

                i += 1

            # =========================
            # 🔗 COMBINE SUBJECT DATA
            # =========================
            subjects = []
            for idx in range(len(codes)):
                subjects.append({
                    "code": codes[idx],
                    "name": names[idx] if idx < len(names) else "",
                    "internal": im[idx] if idx < len(im) else 0,
                    "external": em[idx] if idx < len(em) else 0,
                    "total": total[idx] if idx < len(total) else 0,
                    "result": result[idx] if idx < len(result) else ""
                })

            students.append({
                "roll": roll,
                "name": student_name,
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
