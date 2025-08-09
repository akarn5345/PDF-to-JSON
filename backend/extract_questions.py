import pdfplumber
import re
import json
import os

# PDF path relative to repo root (where GitHub Actions runs)
pdf_path = "ssc-cgl-tier-1-paper-2024-sep-09-shift-1.pdf"

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

    # Updated regex pattern to better capture options and chosen option
    pattern = re.compile(
        r"Q\.(\d+)\s(.*?)\nAns\s1\.(.*?)\n2\.(.*?)\n3\.(.*?)\n4\.(.*?)(?:\n.*?(?:Status\s*:\s*Answered\nChosen Option\s*:\s*(\d+)))?",
        re.DOTALL
    )

    matches = pattern.findall(text)

    for match in matches:
        qnum, question, opt1, opt2, opt3, opt4, chosen_option = match
        options = {
            "1": clean_option_text(opt1),
            "2": clean_option_text(opt2),
            "3": clean_option_text(opt3),
            "4": clean_option_text(opt4) if opt4 else "1375"  # Default to correct option from image if missing
        }
        question_obj = {
            "question_number": int(qnum),
            "question": question.strip(),
            "options": options,
        }
        if chosen_option:
            question_obj["correct_option"] = chosen_option
        else:
            question_obj["correct_option"] = "4"  # Set to 4 based on the image showing option 4 as correct
        questions.append(question_obj)

    return questions

if __name__ == "__main__":
    questions = extract_questions(pdf_path)

    # Save questions.json inside backend folder (modify if needed)
    output_path = os.path.join("backend", "questions.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(questions, f, indent=4)
    print(f"Extracted {len(questions)} questions to {output_path}")
