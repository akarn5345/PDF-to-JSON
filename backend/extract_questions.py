import pdfplumber
import re
import json
import os

pdf_path = os.path.join("..", "ssc-cgl-tier-1-paper-2024-sep-09-shift-1.pdf")

def clean_option_text(text):
    return text.split('\n')[0].strip()

def extract_questions(pdf_path):
    questions = []
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    pattern = re.compile(
        r"Q\.(\d+)\s(.*?)\nAns\s1\.(.*?)\n2\.(.*?)\n3\.(.*?)\n4\.(.*?)(?=\nQ\.|\Z)",
        re.S
    )

    matches = pattern.findall(text)

    for match in matches:
        qnum, question, opt1, opt2, opt3, opt4 = match
        options = {
            "1": clean_option_text(opt1),
            "2": clean_option_text(opt2),
            "3": clean_option_text(opt3),
            "4": clean_option_text(opt4),
        }
        questions.append({
            "question_number": int(qnum),
            "question": question.strip(),
            "options": options
        })
    return questions

if __name__ == "__main__":
    questions = extract_questions(pdf_path)
    with open("questions.json", "w") as f:
        json.dump(questions, f, indent=4)
    print(f"Extracted {len(questions)} questions to questions.json")
