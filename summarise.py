import streamlit as st
import PyPDF2
import google.generativeai as genai
import re

# --- Read PDF ---
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# --- Generate Customized Course ---
def generate_custom_course(content, user_summary, api_key, llm_model):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model)

    prompt = f"""You are an expert course summariser and instructional strategist.
Create a personalized summary on the following course content and user qualification.
User Qualification: {user_summary}
Course Content: {content}
Analyze the Course content and structure it into a summarise format that is engaging for both students and professionals.
include:
A title
A short summary tailored to the user’s background
Examples that relate to their field or experience level
Concept explanations simplified to match the user’s understanding
Optional: Add real-world applications or case studies to make it more practical
Ensure the course is beginner-friendly, practical, and engaging for someone with the given qualification.
This is just a sample structure — feel free to adapt or extend it as needed, while ensuring the tone remains beginner-friendly, practical, and engaging.
Present the output in structured format (e.g., Markdown or bullets).
Format everything in clean Markdown using headers, bold text, bullet points, and code blocks (if necessary)"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Course generation failed: {str(e)}")
        return ""

# --- Split Course into Modules ---
def split_into_modules(course_text):
    pattern = r"(Module\s*\d+[:\-]?\s+.*?)(?=(?:Module\s*\d+[:\-]?\s+)|$)"
    matches = re.findall(pattern, course_text, re.IGNORECASE | re.DOTALL)
    return matches if matches else [course_text]

# --- Generate Summary ---
def generate_summary(text, api_key, model_name):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    prompt = f"""Summarize the following course content in a concise manner, listing the main topics and learning outcomes:

{text[:5000]}"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Summary generation failed: {str(e)}")
        return ""

# --- Streamlit UI ---
st.set_page_config(page_title="Personalised suammry of course", layout="wide")

st.title("📘 Personalised suammry of course")
st.markdown("Upload a course PDF and customize it for a user profile. Get a structured course output and final summary.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📂 Upload Course PDF", type=["pdf"])

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    llm_model = st.selectbox('Gemini Model', ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'])
    api_key = st.text_input('🔐 Gemini API Key', type="password")
    st.markdown("---")
    st.markdown("🧑💻 User Profile")
    user_summary = st.text_area("User Summary", height=150, value="John Doe, 4 years management experience, plant head level")

# Main process
if st.button("🚀 Generate Course"):
    if not api_key:
        st.warning("Please enter your Gemini API Key.")
        st.stop()

    if uploaded_file:
        pdf_content = read_pdf(uploaded_file)
    else:
        st.warning("Please upload a PDF.")
        st.stop()

    with st.spinner("🔍 Customizing course..."):
        custom_course = generate_custom_course(pdf_content, user_summary, api_key, llm_model)

    if custom_course:
        st.subheader("📚 Customized Course Content")
        st.markdown(custom_course)
        st.download_button("⬇️ Download Full Course", custom_course, file_name="custom_course.md")

        st.markdown("---")
        st.header("📌 Course Summary")
        with st.spinner("🧾 Generating summary..."):
            summary = generate_summary(custom_course, api_key, llm_model)
            st.markdown(summary)
