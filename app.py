import PyPDF2
import streamlit as st
import google.generativeai as genai

# Function to read text from PDF
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# Function to generate a custom course using Gemini AI
def generate_custom_course(content, user_summary, api_key, llm_model):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model, generation_config={"frequency_penalty": 1.2})
    
    prompt = f'''Customize the following course content to align with the individual's specific needs, challenges, and professional goals. Ensure that the material is highly relevant, practical, and engaging for their role.
At the beginning, include a concise summary that highlights the key takeaways and benefits tailored for the individual based on the provided context.

User Information:
{user_summary}  

Content:
{content}'''
    
    response = model.generate_content(prompt)
    return response.text

# ---- Streamlit UI ----

st.markdown("<span style='font-size:18px; font-weight:bold;'>📂 Upload a Sample Course PDF file</span>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(" ", type=["pdf"])

llm_model = st.sidebar.selectbox(
    'Please select Model',
    ['gemini-1.5-pro-latest', 'gemini-2.5-pro-exp-03-25', 'gemini-1.5-flash-latest', 'ext-bison-001']
)

api_key = st.sidebar.text_input('Enter your API Key', type="password")

st.markdown("<span style='font-size:18px; font-weight:bold;'>Summarise yourself</span>", unsafe_allow_html=True)
user_summary = st.text_area(
    label=" ",
    height=150,
    value="Hi, my name is John Doe. I have 4 years of experience in management and currently work at a plant head level, overseeing operations and team performance."
)

# ---- Handle Submit ----
if st.button("Submit"):
    if not uploaded_file:
        st.warning("⚠️ Please upload a PDF file first.")
    elif not api_key:
        st.warning("⚠️ Please enter your API key.")
    else:
        st.subheader("🔄 Processing... Please wait.")
        pdf_content = read_pdf(uploaded_file)
        custom_course = generate_custom_course(pdf_content, user_summary, api_key, llm_model)

        # Split summary and details
        summary, *details = custom_course.split("\n\n", 1)

        st.subheader("📌 Summary:")
        st.write(summary)

        st.subheader("📖 Detailed Customized Course Content:")
        st.write("\n\n".join(details) if details else "No additional details provided.")
