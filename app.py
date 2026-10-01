import streamlit as st
import fitz
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import re


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Resume Screener",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Screener")
st.write(
    "A simple resume screening system that compares "
    "candidate resumes with the requirements of a job."
)


# --------------------------------------------------
# SKILLS DATABASE
# --------------------------------------------------

SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "html",
    "css",
    "javascript",
    "machine learning",
    "data science",
    "data analysis",
    "artificial intelligence",
    "deep learning",
    "pandas",
    "matplotlib",
    "excel",
    "communication",
    "leadership",
    "problem solving",
    "teamwork"
]


# --------------------------------------------------
# EDUCATION KEYWORDS
# --------------------------------------------------

EDUCATION_KEYWORDS = [
    "b.tech",
    "btech",
    "b.e",
    "be",
    "b.sc",
    "bsc",
    "m.tech",
    "mtech",
    "m.sc",
    "msc",
    "bachelor",
    "master",
    "computer science",
    "information technology",
    "electronics",
    "electrical"
]


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_pdf_text(file):

    text = ""

    pdf = fitz.open(
        stream=file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


# --------------------------------------------------
# DOCX TEXT EXTRACTION
# --------------------------------------------------

def extract_docx_text(file):

    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# --------------------------------------------------
# EXTRACT TEXT FROM RESUME
# --------------------------------------------------

def extract_text(file):

    if file.name.lower().endswith(".pdf"):

        return extract_pdf_text(file)

    elif file.name.lower().endswith(".docx"):

        return extract_docx_text(file)

    return ""


# --------------------------------------------------
# FIND SKILLS
# --------------------------------------------------

def find_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            found_skills.append(skill)

    return sorted(found_skills)


# --------------------------------------------------
# FIND EXPERIENCE
# --------------------------------------------------

def find_experience(text):

    text = text.lower()

    patterns = [

        r"(\d+)\+?\s*years?\s*(?:of)?\s*experience",

        r"experience\s*[:\-]?\s*(\d+)\+?\s*years?"

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            return int(match.group(1))

    return 0


# --------------------------------------------------
# CHECK EDUCATION
# --------------------------------------------------

def check_education(text):

    text = text.lower()

    for keyword in EDUCATION_KEYWORDS:

        if keyword in text:

            return True

    return False


# --------------------------------------------------
# CALCULATE SKILL SCORE
# --------------------------------------------------

def calculate_skill_score(
    required_skills,
    candidate_skills
):

    if len(required_skills) == 0:

        return 0

    matched = (
        set(required_skills)
        & set(candidate_skills)
    )

    score = (
        len(matched)
        / len(required_skills)
    ) * 100

    return score


# --------------------------------------------------
# JOB REQUIREMENTS
# --------------------------------------------------

st.sidebar.header("Job Requirements")

job_description = st.sidebar.text_area(
    "Enter Job Description",
    height=200
)


# --------------------------------------------------
# DISPLAY REQUIRED SKILLS
# --------------------------------------------------

if job_description:

    required_skills = find_skills(
        job_description
    )

    st.subheader("Required Skills")

    if required_skills:

        st.write(
            ", ".join(required_skills)
        )

    else:

        st.warning(
            "No predefined skills were detected."
        )


# --------------------------------------------------
# UPLOAD RESUMES
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)


# --------------------------------------------------
# SCREENING PROCESS
# --------------------------------------------------

if uploaded_files and job_description:

    required_skills = find_skills(
        job_description
    )

    results = []


    # --------------------------------------------------
    # PROCESS EACH RESUME
    # --------------------------------------------------

    for file in uploaded_files:

        resume_text = extract_text(file)


        # Candidate skills
        candidate_skills = find_skills(
            resume_text
        )


        # Matched skills
        matched_skills = sorted(
            set(required_skills)
            & set(candidate_skills)
        )


        # Missing skills
        missing_skills = sorted(
            set(required_skills)
            - set(candidate_skills)
        )


        # Skill score
        skill_score = calculate_skill_score(
            required_skills,
            candidate_skills
        )


        # Education
        education_found = check_education(
            resume_text
        )

        if education_found:

            education_score = 100

        else:

            education_score = 0


        # Experience
        experience = find_experience(
            resume_text
        )


        if experience >= 3:

            experience_score = 100

        elif experience == 2:

            experience_score = 75

        elif experience == 1:

            experience_score = 50

        else:

            experience_score = 0


        # Overall score
        overall_score = (
            skill_score
            + education_score
            + experience_score
        ) / 3


        # Store candidate result
        results.append({

            "Candidate": file.name,

            "Skill Score": round(
                skill_score,
                2
            ),

            "Education":
                "Yes"
                if education_found
                else "No",

            "Experience":
                experience,

            "Overall Score":
                round(
                    overall_score,
                    2
                ),

            "Matched Skills":
                ", ".join(
                    matched_skills
                )
                if matched_skills
                else "None",

            "Missing Skills":
                ", ".join(
                    missing_skills
                )
                if missing_skills
                else "None"
        })


    # --------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------

    df = pd.DataFrame(results)


    # --------------------------------------------------
    # RANK CANDIDATES
    # --------------------------------------------------

    df = df.sort_values(
        by="Overall Score",
        ascending=False
    ).reset_index(drop=True)


    df.insert(
        0,
        "Rank",
        range(1, len(df) + 1)
    )


    # --------------------------------------------------
    # SCREENING RESULTS
    # --------------------------------------------------

    st.subheader("📊 Screening Results")

    st.dataframe(
        df,
        use_container_width=True
    )


    # --------------------------------------------------
    # CANDIDATE DETAILS
    # --------------------------------------------------

    st.subheader("🔍 Candidate Details")


    for _, row in df.iterrows():

        st.write(
            f"### Rank {row['Rank']}: "
            f"{row['Candidate']}"
        )

        st.write(
            f"**Overall Score:** "
            f"{row['Overall Score']}%"
        )

        st.write(
            f"**Skill Score:** "
            f"{row['Skill Score']}%"
        )

        st.write(
            f"**Education:** "
            f"{row['Education']}"
        )

        st.write(
            f"**Experience:** "
            f"{row['Experience']} years"
        )

        st.write(
            f"**Matched Skills:** "
            f"{row['Matched Skills']}"
        )

        st.write(
            f"**Missing Skills:** "
            f"{row['Missing Skills']}"
        )

        st.divider()


    # --------------------------------------------------
    # SCORE GRAPH
    # --------------------------------------------------

    st.subheader(
        "📈 Candidate Score Comparison"
    )


    fig, ax = plt.subplots()

    ax.bar(
        df["Candidate"],
        df["Overall Score"]
    )

    ax.set_xlabel(
        "Candidates"
    )

    ax.set_ylabel(
        "Overall Score (%)"
    )

    ax.set_title(
        "Resume Screening Scores"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    st.pyplot(fig)


# --------------------------------------------------
# MESSAGE BEFORE SCREENING
# --------------------------------------------------

else:

    st.info(
        "Enter a job description and "
        "upload one or more resumes "
        "to start screening."
    )

