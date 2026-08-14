import pdfplumber
import json
import re
import os

# =========================
# 🔹 Accept any 8-digit roll number starting with 12
# Examples:
# 12345678
# 12456789
# 12999999
# =========================
def is_valid_roll(line):
    line = line.strip()

    if not line:
        return False

    # Extract only the first token (roll number)
    roll = line.split()[0]

    return bool(re.fullmatch(r'12\d{6}', roll))


# =========================
# 🔹 Extract text
# =========================
def extract_text_from_pdf(pdf_path):
    text_data = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_data += "\n" + text

    return text_data


# =========================
# 🔹 Parse text
# =========================
def parse_text(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        if is_valid_roll(lines[i]):

            parts = lines[i].split(" ", 1)
            roll = parts[0]
            name = parts[1] if len(parts) > 1 else "UNKNOWN"

            i += 1
            subjects = []

            while i < len(lines):

                line = lines[i]

                if is_valid_roll(line):
                    break

                if "CGPA" in line:
                    i += 1
                    break

                # Supports:
                # 20-1-101-M
                # R20M29
                # R21M45
                if re.match(r'^(?:\d+-\d+-\d+-|R\d+M\d+)', line):

                    parts = line.split()

                    try:
                        code = parts[0]
                        internal = parts[-6]
                        external = parts[-5]
                        total = parts[-4]
                        result = parts[-3]

                        subject_name = " ".join(parts[1:-6])

                        if result == "AL":
                            result = "F"

                        subjects.append({
                            "code": code,
                            "name": subject_name,
                            "internal": internal,
                            "external": external,
                            "total": total,
                            "result": result
                        })

                    except Exception:
                        pass

                i += 1

            students.append({
                "roll": roll,
                "name": name,
                "subjects": subjects
            })

        else:
            i += 1

    return students


# =========================
# 🔹 Merge Subjects
# Update only if NEW external > OLD external
# =========================
def merge_subjects(old_subjects, new_subjects):

    subject_map = {s["code"]: s for s in old_subjects}

    for new in new_subjects:

        code = new["code"]

        if code not in subject_map:
            subject_map[code] = new
            continue

        old = subject_map[code]

        try:
            old_external = int(old["external"])
        except:
            old_external = -1

        try:
            new_external = int(new["external"])
        except:
            new_external = -1

        if new_external > old_external:
            subject_map[code] = new

    return list(subject_map.values())


# =========================
# 🔹 MAIN
# =========================
def main():

    pdf_folder = "pdfs"

    # -----------------------
    # Load existing JSON
    # -----------------------
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        all_students = {
            s["roll"]: s
            for s in data.get("students", [])
        }

        print("Loaded existing data.json")
    else:
        all_students = {}

    # -----------------------
    # Read PDFs
    # -----------------------
    for root, dirs, files in os.walk(pdf_folder):

        for file in files:

            if not file.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(root, file)

            filename = os.path.splitext(file)[0].lower()

            # Extract semester from filenames like:
            # sem1.pdf
            # sem1_juniors.pdf
            # sem1_supply.pdf
            # sem1_2026.pdf
            # sem1_juniors_supply.pdf
            match = re.match(r'^(sem[1-8])', filename)
            
            if match:
                semester = match.group(1)
            else:
                # If no semX is found, use the filename as-is
                semester = filename

            print(f"Processing {file_path}...")

            text = extract_text_from_pdf(file_path)

            students = parse_text(text)

            for student in students:

                roll = student["roll"]

                if roll not in all_students:

                    all_students[roll] = {
                        "roll": roll,
                        "name": student["name"],
                        "semesters": {}
                    }

                # Update name if empty
                if all_students[roll].get("name", "") == "UNKNOWN":
                    all_students[roll]["name"] = student["name"]

                semesters = all_students[roll]["semesters"]

                if semester not in semesters:

                    semesters[semester] = {
                        "subjects": student["subjects"]
                    }

                else:

                    old_subjects = semesters[semester]["subjects"]

                    semesters[semester]["subjects"] = merge_subjects(
                        old_subjects,
                        student["subjects"]
                    )

    # -----------------------
    # Save JSON
    # -----------------------
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(
            {"students": list(all_students.values())},
            f,
            indent=2,
            ensure_ascii=False
        )

    print("🎉 Done! data.json updated successfully.")


if __name__ == "__main__":
    main()
