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

    # Enhanced regex pattern to handle variations in text layout
    pattern = re.compile(
        r"Q\.(\d+)\s(.*?)(?=\nAns\s1\.)"  # Capture question
        r"\nAns\s1\.(.*?)\n2\.(.*?)\n3\.(.*?)\n4\.(.*?)"  # Capture options
        r"(?:\n.*?(?:Status\s*:\s*Answered\s*Chosen Option\s*:\s*(\d+)|Chosen Option\s*:\s*(\d+)))?",  # Capture chosen option
        re.DOTALL
    )

    matches = pattern.findall(text)

    for match in matches:
        qnum, question, opt1, opt2, opt3, opt4, chosen_opt1, chosen_opt2 = match
        options = {
            "1": clean_option_text(opt1),
            "2": clean_option_text(opt2),
            "3": clean_option_text(opt3),
            "4": clean_option_text(opt4) if opt4 else ""
        }
        question_obj = {
            "question_number": int(qnum),
            "question": question.strip(),
            "options": options,
        }
        # Determine correct_option from either captured group
        chosen_option = chosen_opt1 or chosen_opt2
        question_obj["correct_option"] = chosen_option if chosen_option else None
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
