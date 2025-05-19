import streamlit as st
import PyPDF2
import re
import ollama


#modelname='mistral'
# --- Read PDF ---
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# --- Generate Customized Course using local LLaMA (Ollama) ---
def generate_custom_course(content, user_summary,modelname):
    prompt = f"""You are an expert course summariser and instructional strategist.
Create a personalized summary on the following course content and user qualification.

User Qualification: {user_summary}
Course Content: {content}

Analyze the Course content and structure it into a summarized format that is engaging for both students and professionals.

Include:
- A title
- A short summary tailored to the user’s background
- Examples that relate to their field or experience level
- Concept explanations simplified to match the user’s understanding
- Optional: Add real-world applications or case studies to make it more practical

Ensure the course is beginner-friendly, practical, and engaging for someone with the given qualification.
This is just a sample structure — feel free to adapt or extend it as needed.
Format everything in clean Markdown using headers, bold text, bullet points, and code blocks if needed.
and 
Summarize the course content in a concise manner, listing the main topics and learning outcomes as summary"""

    response = ollama.chat(
        model=modelname,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

# --- Generate Summary using local LLaMA (Ollama) ---
def generate_summary(text,modelname):
    prompt = f"""Summarize the following course content in a concise manner, listing the main topics and learning outcomes:

{text[:5000]}"""

    response = ollama.chat(
        model=modelname,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

# --- Optional: Split Course into Modules ---
def split_into_modules(course_text):
    pattern = r"(Module\s*\d+[:\-]?\s+.*?)(?=(?:Module\s*\d+[:\-]?\s+)|$)"
    matches = re.findall(pattern, course_text, re.IGNORECASE | re.DOTALL)
    return matches if matches else [course_text]

# --- Streamlit UI ---
st.set_page_config(page_title="Personalised Summary of Course", layout="wide")

st.title("📘 Personalised Summary of Course")
st.markdown("Upload a course PDF and customize it for a user profile. Get a structured course output and final summary.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📂 Upload Course PDF", type=["pdf"])

# Sidebar for user profile
with st.sidebar:
    st.header("Models")
    modelname = st.selectbox('Open - Sourced Model', [ 'llama3.1','gemma:7b','mistral','gemma'])
    st.header("🧑💻 User Profile")
    user_summary = st.text_area("User Summary", height=150, value="Based in India, Pratik holds a Master's degree or above qualification and has over 4 years of experience in the Data Science industry. Currently working at a Senior data scientist level.")

# Main process
if st.button("🚀 Generate Course"):
    if not uploaded_file:
        st.warning("Please upload a PDF.")
        st.stop()

    pdf_content = read_pdf(uploaded_file)

    with st.spinner("🔍 Customizing course..."):
        custom_course = generate_custom_course(pdf_content, user_summary,modelname)

    if custom_course:
        st.subheader("📚 Customized Course Content")
        st.markdown(custom_course)
        st.download_button("⬇️ Download Full Course", custom_course, file_name="custom_course.md")

        #st.markdown("---")
        #st.header("📌 Course Summary")
        #'''with st.spinner("🧾 Generating summary..."):
        #    summary = generate_summary(custom_course,modelname)
        #    st.markdown(summary)'''
