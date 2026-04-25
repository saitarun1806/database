import pdfplumber
import json
import re
import os

# Only these prefixes
PREFIXES = ["12316", "12317"]


# =========================
# 🔹 Extract relevant text
# =========================
def extract_text_from_pdf(pdf_path):
    text_data = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text and any(prefix in text for prefix in PREFIXES):
                text_data += "\n" + text

    return text_data


# =========================
# 🔹 Check valid roll
# =========================
def is_valid_roll(line):
    return re.match(r'^(12316\d{3}|12317\d{3})', line)
    # total = 8 digits (5 prefix + 3 digits)


# =========================
# 🔹 Parse one semester
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

                # Next student
                if is_valid_roll(line):
                    break

                # End of student block
                if "CGPA" in line:
                    i += 1
                    break

                # Subject row
                if re.match(r'\d+-\d+-\d+-', line):

                    parts = line.split()

                    try:
                        code = parts[0]
                        internal = parts[-6]
                        external = parts[-5]
                        total = parts[-4]
                        result = parts[-3]

                        subject_name = " ".join(parts[1:-6])

                        # AL → F
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
                        pass  # skip bad lines

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
# 🔹 MAIN MERGE LOGIC
# =========================
def main():
    pdf_folder = "pdfs"
    all_students = {}

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):

            semester = file.replace(".pdf", "")
            file_path = os.path.join(pdf_folder, file)

            print(f"Processing {file}...")

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

                all_students[roll]["semesters"][semester] = {
                    "subjects": student["subjects"]
                }

    # Save JSON
    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("🎉 Done! Both classes merged correctly.")


# =========================
# 🔹 RUN
# =========================
if __name__ == "__main__":
    main()
