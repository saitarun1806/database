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
        # 🎓 Detect TWO rolls (1231 series)
        # =========================
        if (
            i + 1 < len(lines)
            and lines[i].startswith(PREFIX)
            and lines[i+1].startswith(PREFIX)
        ):
            roll1 = lines[i]
            roll2 = lines[i+1]
            i += 2

            block = []

            # =========================
            # 📦 Collect full block
            # =========================
            while i < len(lines) and not lines[i].startswith(PREFIX):
                block.append(lines[i])
                i += 1

            # =========================
            # 🧑‍🎓 Extract Names
            # =========================
            names = [
                l for l in block
                if re.match(r'^[A-Z ]+$', l)
                and len(l.split()) >= 2
                and "CGPA" not in l
                and "SGPA" not in l
            ]

            if len(names) < 2:
                continue

            name1, name2 = names[0], names[1]

            # =========================
            # 📘 Subject Names
            # =========================
            subjects = []
            for l in block:
                if (
                    re.match(r'^[A-Z ]+$', l)
                    and l not in names
                    and "CGPA" not in l
                    and "SGPA" not in l
                ):
                    subjects.append(l)

            n = len(subjects)

            # =========================
            # 🔢 Extract Numbers
            # =========================
            numbers = [int(l) for l in block if l.isdigit()]

            if len(numbers) < n * 6:
                continue

            half = len(numbers) // 2

            nums1 = numbers[:half]
            nums2 = numbers[half:]

            im1 = nums1[:n]
            em1 = nums1[n:2*n]
            total1 = nums1[2*n:3*n]

            im2 = nums2[:n]
            em2 = nums2[n:2*n]
            total2 = nums2[2*n:3*n]

            # =========================
            # 🔤 Results (P/F)
            # =========================
            results = [l for l in block if l in ["P", "F"]]

            rhalf = len(results) // 2
            res1 = results[:rhalf]
            res2 = results[rhalf:]

            # =========================
            # 🔗 Build student data
            # =========================
            def build_student(roll, name, im, em, total, res):
                subs = []
                for j in range(n):
                    subs.append({
                        "name": subjects[j],
                        "internal": im[j] if j < len(im) else 0,
                        "external": em[j] if j < len(em) else 0,
                        "total": total[j] if j < len(total) else 0,
                        "result": res[j] if j < len(res) else ""
                    })
                return {
                    "roll": roll,
                    "name": name,
                    "subjects": subs
                }

            students.append(build_student(roll1, name1, im1, em1, total1, res1))
            students.append(build_student(roll2, name2, im2, em2, total2, res2))

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

            parsed_students = parse_pdf(file_path, semester)

            for student in parsed_students:
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
    # 💾 Save JSON
    # =========================
    with open("data.json", "w") as f:
        json.dump({"students": list(all_students.values())}, f, indent=2)

    print("✅ data.json generated successfully!")


if __name__ == "__main__":
    main()
