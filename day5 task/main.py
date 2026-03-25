import os
import re
import json
import logging
from docx import Document
import PyPDF2

logging.basicConfig(
    filename="logs/extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(msg):
    logging.info(msg)

class ResumeExtractor:

    def extract_text(self, file_path):
        if file_path.endswith(".pdf"):
            return self.extract_pdf(file_path)
        elif file_path.endswith(".docx"):
            return self.extract_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

    def extract_pdf(self, file_path):
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        return text

    def extract_docx(self, file_path):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def clean_text(self, text):
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[^\w\s.,@+-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def normalize_text(self, text):
        text = text.lower()
        text = text.replace("•", "-")
        return text

    def extract_sections(self, text):
        sections = {"education": "", "experience": "", "skills": ""}
        current_section = None
        words = text.split(" ")

        for word in words:
            if "education" in word:
                current_section = "education"
            elif "experience" in word:
                current_section = "experience"
            elif "skills" in word:
                current_section = "skills"
            elif current_section:
                sections[current_section] += word + " "

        return sections

    def process_resume(self, file_path):
        try:
            log(f"Processing: {file_path}")
            raw_text = self.extract_text(file_path)
            cleaned = self.clean_text(raw_text)
            normalized = self.normalize_text(cleaned)
            sections = self.extract_sections(normalized)

            return {
                "file_name": os.path.basename(file_path),
                "text": normalized,
                "sections": sections
            }
        except Exception as e:
            log(f"Error processing {file_path}: {str(e)}")
            return None


def run_pipeline():
    extractor = ResumeExtractor()
    input_folder = "resumes"
    output_folder = "output"

    os.makedirs(output_folder, exist_ok=True)

    results_log = []

    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)

        result = extractor.process_resume(file_path)

        if result:
            output_file = os.path.join(output_folder, file + ".json")
            with open(output_file, "w") as f:
                json.dump(result, f, indent=4)

            print(f"Processed: {file}")
            results_log.append(f"{file} - Success")
        else:
            print(f"Failed: {file}")
            results_log.append(f"{file} - Failed")

    with open("logs/test_results.txt", "w") as f:
        for line in results_log:
            f.write(line + "\n")


if __name__ == "__main__":
    run_pipeline()
