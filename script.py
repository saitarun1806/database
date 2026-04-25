import json
import re
import os
from pdfminer.high_level import extract_text

PREFIX = "1231"

# =========================
# 🔹 TYPE A PARSER (MAIN FORMAT)
# =========================
def parse_type_a(lines, i):
    students = []

    roll = lines[i]
    i += 1

    block = []
    while i < len(lines) and not re.match(r'^1231\d{4}$', lines[i]):
        block.append(lines[i])
        i += 1

    # -------------------------
    # SUBJECT CODES
    # -------------------------
    codes = [l for l in block if re.match(r'\d+-\d+-\d+-', l)]
    n = len(codes)

    # -------------------------
    # STUDENT NAME
    # -------------------------
    name = "UNKNOWN"
    for l in block:
        if re.match(r'^[A-Z .]+$', l) and len(l.split()) >= 2:
            if not any(x in l for x in ["CGPA", "SGPA", "TOTAL", "GRADE"]):
                name = l
                break

    # -------------------------
    # SUBJECT NAMES
    # -------------------------
    subjects = []
    found_name = False

    for l in block:
        if l == name:
            found_name = True
            continue

        if found_name and len(subjects) < n:
            if re.match(r'^[A-Z ]+$', l):
                subjects.append(l)

    # -------------------------
    # VALUES (IM, EM, TOTAL)
    # -------------------------
    values = [l for l in block if l.isdigit() or l in ["AL", "-"]]

    im = values[:n]
    em = values[n:2*n]
    total = values[2*n:3*n]

    # -------------------------
    # RESULTS (P/F)
    # -------------------------
    results = [l for l in block if l in ["P", "F"]]

    # -------------------------
    # BUILD SUBJECT DATA
    # -------------------------
    subs = []

    for j in range(n):

        internal = im[j] if j < len(im) else ""
        external = em[j] if j < len(em) else ""
        tot = total[j] if j < len(total) else ""

        # 🔥 RESULT LOGIC
        if j < len(results):
            result = results[j]
        else:
            if internal == "AL" or external == "AL":
                result = "F"
            else:
                try:
                    if int(tot) < 40:
                        result = "F"
                    else:
                        result = "P"
                except:
                    result = ""

        subs.append({
            "code": codes[j] if j < len(codes) else "",
            "name": subjects[j] if j < len(subjects) else "",
            "internal": internal,
            "external": external,
            "total": tot,
            "result": result
        })

    students.append({
        "roll": roll,
        "name": name,
        "subjects": subs
    })

    return students, i


# =========================
# 🔹 TYPE B PARSER (fallback)
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

            # handle AL
            if im == "AL" or em == "AL":
                res = "F"

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
# 🔹 MAIN PARSER
# =========================
def parse_pdf(file_path, semester):
    text = extract_text(file_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        if re.match(r'^1231\d{4}$', lines[i]):

            # detect structure
            next_lines = lines[i:i+20]

            # if many subject codes → type A
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

    # SAVE JSON
    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("✅ FINAL data.json generated successfully!")


if __name__ == "__main__":
    main()
