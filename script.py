import pdfplumber
import json
import re
import os

PREFIX = "1231"


# =========================
# 🔹 Extract only relevant pages
# =========================
def extract_text_from_pdf(pdf_path):
    text_data = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text and PREFIX in text:
                text_data += "\n" + text

    return text_data


# =========================
# 🔹 Parse text → students
# =========================
def parse_text(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    while i < len(lines):

        # 🎓 detect student
        if re.match(r'^1231\d{4}', lines[i]):

            parts = lines[i].split(" ", 1)
            roll = parts[0]
            name = parts[1] if len(parts) > 1 else "UNKNOWN"

            i += 1
            subjects = []

            while i < len(lines):

                line = lines[i]

                # next student
                if re.match(r'^1231\d{4}', line):
                    break

                # stop at summary
                if "CGPA" in line:
                    i += 1
                    break

                # subject row
                if re.match(r'\d+-\d+-\d+-', line):

                    parts = line.split()

                    code = parts[0]
                    internal = parts[-6]
                    external = parts[-5]
                    total = parts[-4]
                    result = parts[-3]

                    subject_name = " ".join(parts[1:-6])

                    # 🔥 AL → F
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
# 🔹 MAIN FUNCTION (SECTION-WISE SAFE MERGE)
# =========================
def main():
    pdf_folder = "pdfs"
    data_file = "data.json"

    # =========================
    # 🔹 Load existing JSON
    # =========================
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            existing_data = json.load(f)
            all_students = {
                f"{s['section']}_{s['roll']}": s
                for s in existing_data.get("students", [])
            }
    else:
        all_students = {}

    # =========================
    # 🔹 Process ALL PDFs
    # =========================
    for root, dirs, files in os.walk(pdf_folder):
        for file in files:
            if file.endswith(".pdf"):

                semester = file.replace(".pdf", "")
                file_path = os.path.join(root, file)

                # 🔥 detect section from folder
                section = os.path.basename(root)

                # if file directly inside pdfs/, name it MAIN
                if section == "pdfs":
                    section = "MAIN"

                print(f"📄 Processing {file_path} (Section: {section})")

                text = extract_text_from_pdf(file_path)
                students = parse_text(text)

                for student in students:
                    key = f"{section}_{student['roll']}"

                    # create student if not exists
                    if key not in all_students:
                        all_students[key] = {
                            "roll": student["roll"],
                            "name": student["name"],
                            "section": section,
                            "semesters": {}
                        }

                    # =========================
                    # 🔥 SAFE SEMESTER MERGE
                    # =========================
                    if semester not in all_students[key]["semesters"]:
                        all_students[key]["semesters"][semester] = {
                            "subjects": student["subjects"]
                        }
                        print(f"✅ Added {student['roll']} ({section}) {semester}")

                    else:
                        existing_subjects = all_students[key]["semesters"][semester]["subjects"]

                        existing_codes = {sub["code"] for sub in existing_subjects}

                        new_subjects = [
                            sub for sub in student["subjects"]
                            if sub["code"] not in existing_codes
                        ]

                        if new_subjects:
                            existing_subjects.extend(new_subjects)
                            print(f"🔄 Updated {student['roll']} ({section}) {semester}")
                        else:
                            print(f"⏭ Skipped {student['roll']} ({section}) {semester}")

    # =========================
    # 💾 Save final JSON
    # =========================
    with open(data_file, "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("\n🎉 Data updated with section separation!")


# =========================
# 🔹 RUN
# =========================
if __name__ == "__main__":
    main()
