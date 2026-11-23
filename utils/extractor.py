import re
import pdfplumber
from docx import Document


def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(file):
    text = ""
    try:
        doc = Document(file)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text += row_text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text


def extract_resume_text(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    return ""


def extract_contact_info(text):
    email_pattern = r"\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Za-z]{2,}\b"
    email_matches = re.findall(email_pattern, text)
    email = re.sub(r"\s+", "", email_matches[0]) if email_matches else "Not Found"

    normalized_text = re.sub(r"[ \t]+", " ", text)

    pk_matches = re.findall(
        r"(?:\+92[\s.-]?|0092[\s.-]?|0)?3\d{2}[\s.-]?\d{7}",
        normalized_text,
    )
    for match in pk_matches:
        cleaned = re.sub(r"\s+", " ", match).strip()
        digits = re.sub(r"\D", "", cleaned)
        if 10 <= len(digits) <= 13:
            return email, cleaned

    labeled_matches = re.findall(
        r"(?:phone|mobile|cell|tel|telephone|contact|call)[^\n\d]{0,20}(\+?\d[\d\s().-]{7,20}\d)",
        normalized_text,
        flags=re.IGNORECASE,
    )

    general_matches = re.findall(
        r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}",
        normalized_text,
    )

    for candidate in labeled_matches + general_matches:
        cleaned_candidate = re.sub(r"\s+", " ", candidate).strip()
        digits_only = re.sub(r"\D", "", cleaned_candidate)
        if 10 <= len(digits_only) <= 15:
            return email, cleaned_candidate

    compact_text = re.sub(r"[\s().-]+", "", text)
    compact_pk = re.findall(r"(?:\+?92|0)?3\d{9}", compact_text)
    if compact_pk:
        return email, compact_pk[0]

    return email, "Not Found"


def calculate_match_score(resume_text, job_description):
    if not job_description.strip() or not resume_text.strip():
        return 0, []

    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower()))
    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", resume_text.lower()))

    if not jd_words:
        return 0, []

    common_words = jd_words.intersection(resume_words)
    score = min(int((len(common_words) / len(jd_words)) * 100), 100)
    return score, sorted(list(common_words))[:8]