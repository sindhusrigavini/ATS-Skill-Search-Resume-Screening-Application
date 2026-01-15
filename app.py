import streamlit as st
import pandas as pd
import pdfplumber
import docx
import re
from io import BytesIO

st.set_page_config(page_title="ATS Skill Search", layout="wide")

# ------------------------------------------
# SKILL EXTRACTION FUNCTION
# ------------------------------------------
COMMON_SKILLS = [
    "python", "java", "javascript", "react", "node", "angular", "sql", "html",
    "css", "aws", "docker", "kubernetes", "flask", "django", "excel",
    "powerbi", "tableau", "gcp", "azure", "mongodb", "redis"
]

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


def clean_and_extract_skills(text):
    text = text.lower()
    found = []

    for skill in COMMON_SKILLS:
        if re.search(rf"\b{skill}\b", text):
            found.append(skill)

    return ", ".join(found)


# ------------------------------------------
# STREAMLIT UI
# ------------------------------------------
st.title("🔎 ATS Skill Search")

uploaded_files = st.file_uploader("Upload Resume Files (PDF or DOCX)", 
                                  type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} resumes uploaded successfully!")

# Button to process resumes
if st.button("Process Resumes"):
    if not uploaded_files:
        st.error("Please upload resumes first!")
    else:
        all_rows = []

        for file in uploaded_files:
            file_name = file.name

            if file_name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)

            skills = clean_and_extract_skills(text)

            all_rows.append({
                "File Name": file_name,
                "Extracted Skills": skills,
            })

        df = pd.DataFrame(all_rows)

        st.subheader("📄 Extracted Resume Data")
        st.dataframe(df)

        # Save in session for search use
        st.session_state["df"] = df


# ------------------------------------------
# SEARCH SKILLS
# ------------------------------------------
st.subheader("🔍 Enter Required Skills")

required_input = st.text_input("Enter skills (comma separated)", placeholder="python, sql")

def match_skills(cell, required_skills):
    if not isinstance(cell, str) or cell.strip() == "":
        return False

    resume_skills = [s.strip().lower() for s in cell.split(",")]
    return all(skill in resume_skills for skill in required_skills)


if st.button("Search Candidates"):
    if "df" not in st.session_state:
        st.error("Please upload and process resumes first!")
    else:
        df = st.session_state["df"]

        required = [s.strip().lower() for s in required_input.split(",") if s.strip()]

        if not required:
            st.error("Enter at least one skill!")
        else:
            matched = df[df["Extracted Skills"].apply(lambda x: match_skills(x, required))]

            st.subheader("Search Results")
            if matched.empty:
                st.warning("❌ No matching candidates found.")
            else:
                st.success(f"✅ {len(matched)} candidates found")
                st.dataframe(matched)