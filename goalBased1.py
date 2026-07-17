import streamlit as st
import os
import re
import fitz
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI


# -------- LOAD ENV --------

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


# -------- GLOBAL STORAGE --------

application_info = {
    "name": None,
    "email": None,
    "skills": None
}


# -------- FUNCTIONS --------

def extract_application_info(text):

    name_match = re.search(
        r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        text,
        re.IGNORECASE
    )

    email_match = re.search(
        r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        text
    )

    skills_match = re.search(
        r"(?:skills are|i know|i can use)\s+(.+)",
        text,
        re.IGNORECASE
    )

    if name_match:
        application_info["name"] = name_match.group(1)

    if email_match:
        application_info["email"] = email_match.group(0)

    if skills_match:
        application_info["skills"] = skills_match.group(1)


def extract_text_from_pdf(uploaded_file):

    doc = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text


def extract_info_from_cv(text):

    email_match = re.search(
        r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        text
    )

    if email_match:
        application_info["email"] = email_match.group(0)

    skills_section = re.search(
        r"Skills(.*)",
        text,
        re.DOTALL
    )

    if skills_section:

        skills = skills_section.group(1)

        skills = skills.replace("\n", ", ")

        application_info["skills"] = skills[:200]


def check_missing():

    return [

        k for k, v in application_info.items()

        if not v
    ]


# -------- STREAMLIT UI --------

st.set_page_config(

    page_title="Job Assistant"
)

st.title("🎯 Job Application Assistant")


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# -------- FILE UPLOAD --------

resume = st.sidebar.file_uploader(

    "Upload Resume",

    type=["pdf"]
)


if resume:

    text = extract_text_from_pdf(resume)

    extract_info_from_cv(text)

    st.sidebar.success("Resume processed")


# -------- CHAT --------

user_input = st.chat_input(

    "Type your details..."
)


if user_input:

    st.session_state.chat_history.append(

        ("user", user_input)
    )

    extract_application_info(user_input)

    missing = check_missing()

    if not missing:

        reply = f"""
✅ Application Ready

Name: {application_info['name']}
Email: {application_info['email']}
Skills: {application_info['skills']}
"""

    else:

        prompt = f"""

User message:
{user_input}

We are collecting job application info.

Already collected:
{application_info}

Missing fields:
{missing}

Ask user ONLY for missing fields.
Keep response short.
"""

        response = llm.invoke(prompt)

        reply = response.content


    st.session_state.chat_history.append(

        ("assistant", reply)
    )


# -------- DISPLAY CHAT --------

for sender, msg in st.session_state.chat_history:

    with st.chat_message(sender):

        st.markdown(msg)
        print(os.getenv("GOOGLE_API_KEY"))