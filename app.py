import io
import re
import time
import pandas as pd
import streamlit as st
from openpyxl.utils import get_column_letter
from utils.extractor import extract_resume_text, extract_contact_info, calculate_match_score
from utils.mailer import send_shortlist_email

st.set_page_config(
    page_title="Automated Resume Screener - Rhombix Technologies",
    layout="wide"
)

def extract_candidate_name(resume_text, file_name):
    ignore_words = {
        "resume", "curriculum", "vitae", "cv", "profile", "summary",
        "objective", "contact", "email", "phone", "mobile", "address",
        "location", "city", "country", "skills", "education",
        "experience", "projects", "linkedin", "github"
    }

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]

    for line in lines[:10]:
        labeled = re.match(r"^\s*name\s*[:\-–—]\s*(.+)$", line, flags=re.IGNORECASE)
        if labeled:
            raw_name = labeled.group(1).strip()
            if "@" not in raw_name and not any(ch.isdigit() for ch in raw_name):
                cleaned = re.sub(r"[^A-Za-z.\s]", "", raw_name)
                cleaned = re.sub(r"\s+", " ", cleaned).strip()
                if cleaned:
                    return cleaned

    for line in lines[:8]:
        if "@" in line or any(char.isdigit() for char in line):
            continue

        line_without_prefix = re.sub(r"^\s*name\s*:?\s*", "", line, flags=re.IGNORECASE).strip()
        cleaned_line = re.sub(r"[^A-Za-z.\s]", "", line_without_prefix)
        cleaned_line = re.sub(r"\s+", " ", cleaned_line).strip()
        words = [w for w in cleaned_line.split() if w.lower().rstrip(".") not in ignore_words]

        if 1 <= len(words) <= 5:
            return " ".join(words)

    base_name = file_name.rsplit(".", 1)[0]
    base_name = re.sub(r"[_\-.]+", " ", base_name)
    base_name = re.sub(r"\b(resume|cv|final|updated|document)\b", "", base_name, flags=re.IGNORECASE)
    base_name = re.sub(r"\s+", " ", base_name).strip()
    return base_name if base_name else "Candidate"


st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 14px; padding: 12px 16px;
                border-radius: 12px; background: rgba(59, 130, 246, 0.08);
                border: 1px solid rgba(59, 130, 246, 0.25); margin-bottom: 14px;">
        <div style="background: #2563eb; color: white; width: 46px; height: 46px;
                    border-radius: 10px; display: flex; align-items: center; justify-content: center;
                    flex-shrink: 0;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.6rem;">Automated Resume Screener</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Job Requirements")
job_description = st.sidebar.text_area(
    "Enter Job Description / Required Skills:",
    height=160,
    placeholder="e.g., Python, SQL, FastAPI, Machine Learning, 2 years experience..."
)

threshold_score = st.sidebar.slider("Minimum Shortlist Score (%)", 0, 100, 35)

st.sidebar.markdown("---")
st.sidebar.header("📧 Email Alerts")

sender_email = ""
sender_password = ""

try:
    sender_email = st.secrets.get("EMAIL_SENDER", "")
    sender_password = st.secrets.get("EMAIL_PASSWORD", "")
except Exception:
    sender_email = ""
    sender_password = ""

auto_email_enabled = st.sidebar.checkbox("Send email automatically to shortlisted candidates", value=True)

st.subheader("📁 Upload Resumes (PDF or DOCX)")
uploaded_files = st.file_uploader(
    "Select one or more resume files (PDF or DOCX):",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files and job_description.strip():
    if st.button("Run Screening"):
        results = []

        with st.spinner("Screening resumes and sending shortlist notifications..."):
            for file in uploaded_files:
                resume_text = extract_resume_text(file)
                candidate_name = extract_candidate_name(resume_text, file.name)
                email, phone = extract_contact_info(resume_text)
                score, matched_keywords = calculate_match_score(resume_text, job_description)
                status = "Shortlisted" if score >= threshold_score else "Rejected"

                email_status = "Not Sent"
                if status == "Shortlisted" and auto_email_enabled:
                    if not sender_email or not sender_password:
                        email_status = "Credentials Missing"
                    elif email == "Not Found":
                        email_status = "No Email Found"
                    else:
                        sent = send_shortlist_email(email, candidate_name, sender_email, sender_password)
                        email_status = "Sent" if sent else "Failed"
                        time.sleep(0.25)

                results.append({
                    "Candidate Name": candidate_name,
                    "File Name": file.name,
                    "Email": email,
                    "Phone": phone,
                    "Match Score (%)": score,
                    "Status": status,
                    "Email Status": email_status,
                    "Matched Keywords": ", ".join(matched_keywords)
                })

        df = pd.DataFrame(results)
        st.success("Screening complete!")

        total_count = len(df)
        shortlisted_count = int((df["Status"] == "Shortlisted").sum())
        rejected_count = total_count - shortlisted_count

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Resumes Scanned", total_count)
        col2.metric("Shortlisted Candidates", shortlisted_count)
        col3.metric("Rejected Candidates", rejected_count)

        st.dataframe(df, width="stretch")

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            sheet_name = "Screening Results"
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]

            for col_idx, column_cells in enumerate(worksheet.columns, start=1):
                max_length = 0
                for cell in column_cells:
                    val_str = str(cell.value) if cell.value is not None else ""
                    max_length = max(max_length, len(val_str))
                col_letter = get_column_letter(col_idx)
                worksheet.column_dimensions[col_letter].width = min(max(max_length + 6, 16), 55)

            for row in worksheet.iter_rows():
                worksheet.row_dimensions[row[0].row].height = 24

        st.download_button(
            label="Download Excel Report (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name="resume_screening_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif uploaded_files and not job_description.strip():
    st.warning("Please enter a Job Description in the sidebar before running screening.")