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

        # =========================
        # 🎯 Detect two students
        # =========================
        if (
            i + 1 < len(lines)
            and lines[i].startswith(PREFIX)
            and lines[i+1].startswith(PREFIX)
        ):
            roll1 = lines[i]
            roll2 = lines[i+1]
            i += 2

            # =========================
            # 📘 Detect SUBJECT COUNT dynamically
            # =========================
            codes1 = []
            while i < len(lines) and re.match(r'\d+-\d+-\d+-\w+', lines[i]):
                codes1.append(lines[i])
                i += 1

            subject_count = len(codes1)

            # next same count belongs to student 2
            codes2 = lines[i:i+subject_count]
            i += subject_count

            # =========================
            # 🧑‍🎓 NAME + SUBJECTS
            # =========================
            name1 = lines[i]; i += 1
            subjects1 = lines[i:i+subject_count]; i += subject_count

            name2 = lines[i]; i += 1
            subjects2 = lines[i:i+subject_count]; i += subject_count

            # =========================
            # 🔢 STUDENT 1 MARKS
            # =========================
            im1 = lines[i:i+subject_count]; i += subject_count
            em1 = lines[i:i+subject_count]; i += subject_count
            total1 = lines[i:i+subject_count]; i += subject_count
            res1 = lines[i:i+subject_count]; i += subject_count

            # =========================
            # ⏭️ SKIP TOTAL BLOCK
            # =========================
            while i < len(lines) and not lines[i].isdigit():
                i += 1

            # =========================
            # 🔢 STUDENT 2 MARKS
            # =========================
            im2 = lines[i:i+subject_count]; i += subject_count
            em2 = lines[i:i+subject_count]; i += subject_count
            total2 = lines[i:i+subject_count]; i += subject_count
            res2 = lines[i:i+subject_count]; i += subject_count

            # =========================
            # 🔗 BUILD FUNCTION
            # =========================
            def build(roll, name, codes, subjects, im, em, total, res):
                subs = []
                for j in range(subject_count):
                    subs.append({
                        "code": codes[j] if j < len(codes) else "",
                        "name": subjects[j] if j < len(subjects) else "",
                        "internal": im[j] if j < len(im) else "",
                        "external": em[j] if j < len(em) else "",
                        "total": total[j] if j < len(total) else "",
                        "result": res[j] if j < len(res) else ""
                    })
                return {
                    "roll": roll,
                    "name": name,
                    "subjects": subs
                }

            students.append(build(roll1, name1, codes1, subjects1, im1, em1, total1, res1))
            students.append(build(roll2, name2, codes2, subjects2, im2, em2, total2, res2))

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
