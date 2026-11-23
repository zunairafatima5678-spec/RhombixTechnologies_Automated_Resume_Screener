# RhombixTechnologies_Automated_Resume_Screener

# 📄 Automated Resume Screener

An automated resume screening web application built with **Python** and **Streamlit**, created as part of project tasks with **Rhombix Technologies**.

## 🚀 Features
- **Resume Parsing:** Extracts text from **PDF** and **DOCX** resume files for fast candidate screening.
- **Contact & Candidate Extraction:** Automatically identifies candidate names, email addresses, and phone numbers.
- **Keyword Matching & Scoring:** Compares resume content against job requirements and calculates a match score percentage.
- **Shortlisting & Excel Export:** Marks candidates as **Shortlisted** or **Rejected** based on the minimum score threshold and exports a clean, auto-fitted Excel report (`.xlsx`).
- **Automated Email Notifications:** Sends professional selection emails from **Rhombix Technologies** to shortlisted candidates via Gmail SMTP.

## 🛠️ Tech Stack
- **Python** (Core Screening & Email Logic)
- **Streamlit** (Interactive Web Interface)
- **Pandas & OpenPyXL** (Data Processing & Excel Export)
- **pdfplumber & python-docx** (PDF and DOCX Text Extraction)

## ⚙️ Installation & Running Guide

To run this project locally on your machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/zunairafatima5678-spec/RhombixTechnologies_Automated_Resume_Screener](https://github.com/zunairafatima5678-spec/RhombixTechnologies_Automated_Resume_Screener)
   cd RhombixTechnologies_Automated_Resume_Screener

```

2. **Install Dependencies:**
Make sure you have Python installed, then run the `requirements.txt` file to install the required libraries:
```bash
pip install -r requirements.txt

```


3. **Configure Secrets (Optional for Email Alerts):**
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your Gmail credentials:
```toml
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_16_digit_app_password"

```


> **Note:** To use Gmail SMTP email notifications, you must enable **2-Step Verification** on your Google account and generate a **16-digit App Password** to use in `EMAIL_PASSWORD`.


4. **Run the Application:**
Execute the Streamlit app:
```bash
streamlit run app.py

```


5. **Use the App:**
Open your web browser and click on the local URL provided in your terminal (e.g., `http://localhost:8501`).

```

