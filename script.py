import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

# =========================
# 🔹 Parser A: Two-student structure
# =========================
def parse_type_a(lines, i):
    students = []

    roll1 = lines[i]
    i += 1

    block = []
    while i < len(lines) and not re.match(r'^1231\d{4}$', lines[i]):
        block.append(lines[i])
        i += 1

    # detect subject codes
    codes = [l for l in block if re.match(r'\d+-\d+-\d+-', l)]
    n = len(codes)

    # names
    names = [
        l for l in block
        if re.match(r'^[A-Z .]+$', l)
        and len(l.split()) >= 2
        and "CGPA" not in l
    ]

    # values
    values = [l for l in block if l.isdigit() or l in ["AL", "-"]]
    results = [l for l in block if l in ["P", "F"]]

    # subjects
    subjects = [
        l for l in block
        if re.match(r'^[A-Z ]+$', l)
        and l not in names
        and "CGPA" not in l
        and "GRADE" not in l
    ]

    if not names:
        return [], i

    name = names[0]

    im = values[:n]
    em = values[n:2*n]
    total = values[2*n:3*n]

    subs = []
    for j in range(n):
        subs.append({
            "code": codes[j] if j < len(codes) else "",
            "name": subjects[j] if j < len(subjects) else "",
            "internal": im[j] if j < len(im) else "",
            "external": em[j] if j < len(em) else "",
            "total": total[j] if j < len(total) else "",
            "result": results[j] if j < len(results) else ""
        })

    students.append({
        "roll": roll1,
        "name": name,
        "subjects": subs
    })

    return students, i


# =========================
# 🔹 Parser B: Clean single student
# =========================
def parse_type_b(lines, i):
    roll = lines[i]
    i += 1

    name = "UNKNOWN"
    subjects = []

    if i < len(lines):
        name = lines[i]
        i += 1

    while i < len(lines) and not re.match(r'^1231\d{4}$', lines[i]):
        if re.match(r'\d+-\d+-\d+-', lines[i]):
            code = lines[i]
            sub = lines[i+1] if i+1 < len(lines) else ""
            im = lines[i+2] if i+2 < len(lines) else ""
            em = lines[i+3] if i+3 < len(lines) else ""
            total = lines[i+4] if i+4 < len(lines) else ""
            res = lines[i+5] if i+5 < len(lines) else ""

            subjects.append({
                "code": code,
                "name": sub,
                "internal": im,
                "external": em,
                "total": total,
                "result": res
            })

            i += 6
        else:
            i += 1

    return [{
        "roll": roll,
        "name": name,
        "subjects": subjects
    }], i


# =========================
# 🔹 MAIN PARSER (AUTO DETECT)
# =========================
def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        if re.match(r'^1231\d{4}$', lines[i]):

            # 🔍 Detect structure
            next_lines = lines[i:i+20]

            # if many codes ahead → Type A
            if sum(1 for l in next_lines if re.match(r'\d+-\d+-\d+-', l)) > 3:
                parsed, i = parse_type_a(lines, i)
                students.extend(parsed)

            else:
                parsed, i = parse_type_b(lines, i)
                students.extend(parsed)

        else:
            i += 1

    return students


# =========================
# 🔹 MAIN FUNCTION
# =========================
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

    print("✅ FINAL multi-structure parsing complete!")


if __name__ == "__main__":
    main()
