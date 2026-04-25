import pdfplumber
import json
import re
import os


# =========================
# 🔹 Extract text (no filter now)
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
# 🔹 Generic parser (prefix-based)
# =========================
def parse_text_by_prefix(text, prefix):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    students = []
    i = 0

    pattern = rf'^{prefix}\d+'

    while i < len(lines):

        if re.match(pattern, lines[i]):

            parts = lines[i].split(" ", 1)
            roll = parts[0]
            name = parts[1] if len(parts) > 1 else "UNKNOWN"

            i += 1
            subjects = []

            while i < len(lines):

                line = lines[i]

                # next student
                if re.match(pattern, line):
                    break

                # end block
                if "CGPA" in line:
                    i += 1
                    break

                # subject line
                if re.match(r'\d+-\d+-\d+-', line):

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

                    except:
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
# 🔹 Merge helper
# =========================
def merge_students(all_students, students, semester):
    for student in students:
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


# =========================
# 🔹 MAIN
# =========================
def main():
    pdf_folder = "pdfs"

    data1 = {}  # for 12316
    data2 = {}  # for 12317

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):

            semester = file.replace(".pdf", "")
            file_path = os.path.join(pdf_folder, file)

            print(f"Processing {file}...")

            text = extract_text_from_pdf(file_path)

            # 🔹 Parse separately
            students_12316 = parse_text_by_prefix(text, "12316")
            students_12317 = parse_text_by_prefix(text, "12317")

            merge_students(data1, students_12316, semester)
            merge_students(data2, students_12317, semester)

    # 🔹 Final merge
    final_students = list(data1.values()) + list(data2.values())

    # 🔹 Save
    with open("data.json", "w") as f:
        json.dump({"students": final_students}, f, indent=2)

    print("🎉 Done! Both datasets merged into data.json")


# =========================
# 🔹 RUN
# =========================
if __name__ == "__main__":
    main()
