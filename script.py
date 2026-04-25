import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

# ✅ Keep AL / - and convert numbers only
def clean_value(x):
    x = x.strip()

    if x in ["AL", "-"]:
        return x

    if x.isdigit():
        return int(x)

    return x


def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # 🔍 Find all roll numbers (only 1231)
    roll_indices = []
    for i, line in enumerate(lines):
        if line.startswith(PREFIX) and line.isdigit():
            roll_indices.append(i)

    students = []

    # =========================
    # 🔄 Process each student block
    # =========================
    for idx in range(len(roll_indices)):
        start = roll_indices[idx]
        end = roll_indices[idx + 1] if idx + 1 < len(roll_indices) else len(lines)

        block = lines[start:end]
        roll = block[0]

        # =========================
        # 🧑‍🎓 Extract name
        # =========================
        name = "UNKNOWN"
        for l in block:
            if re.match(r'^[A-Z .]+$', l) and len(l.split()) >= 2:
                if not any(x in l for x in ["CGPA", "SGPA", "TOTAL", "GRADE"]):
                    name = l
                    break

        # =========================
        # 📘 Extract subjects
        # =========================
        subjects = []
        for l in block:
            if re.match(r'^[A-Z ]+$', l) and l != name:
                if not any(x in l for x in ["CGPA", "SGPA", "TOTAL", "GRADE"]):
                    subjects.append(l)

        n = len(subjects)

        # =========================
        # 🔢 Extract values (IM, EM, TOTAL)
        # =========================
        values = [
            clean_value(l)
            for l in block
            if l.isdigit() or l in ["AL", "-"]
        ]

        im = values[:n]
        em = values[n:2*n]
        total = values[2*n:3*n]

        # =========================
        # 🔤 Extract results
        # =========================
        results = [l for l in block if l in ["P", "F"]]

        # =========================
        # 🔗 Combine everything
        # =========================
        subs = []
        for i in range(n):
            subs.append({
                "name": subjects[i] if i < len(subjects) else "",
                "internal": im[i] if i < len(im) else "",
                "external": em[i] if i < len(em) else "",
                "total": total[i] if i < len(total) else "",
                "result": results[i] if i < len(results) else ""
            })

        students.append({
            "roll": roll,
            "name": name,
            "subjects": subs
        })

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

    # 💾 Save final JSON
    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("✅ FINAL data.json generated successfully!")


if __name__ == "__main__":
    main()
