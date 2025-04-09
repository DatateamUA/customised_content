import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import re

# --- Read PDF ---
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# --- Extract JSON from Gemini Output ---
def extract_json_from_response(response_text):
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("Gemini returned no valid JSON.")

# --- Generate Mind Map JSON ---
def generate_mindmap_data(content, api_key, model_name):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""Convert this course content into a mindmap structure. Return ONLY valid JSON with:
    - "nodes" (list of {{"id", "label", "group"}})
    - "edges" (list of {{"from", "to", "label"}})
    
    Content: {content[:3000]}"""  # Truncate to fit context length
    
    try:
        response = model.generate_content(prompt)
        return extract_json_from_response(response.text)
    except Exception as e:
        st.error(f"❌ Mindmap generation failed: {str(e)}")
        return None

# --- Visualize Mind Map ---
def visualize_mindmap(data):
    if not data or "nodes" not in data:
        st.warning("⚠️ Invalid mindmap data.")
        return

    nodes = [{"id": n["id"], "label": n["label"], "group": n.get("group", "default")} for n in data["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in data["edges"]]

    html = f"""
    <html>
    <head>
      <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
      <style>
        #mynetwork {{
          width: 100%;
          height: 500px;
          border: 1px solid #e0e0e0;
          background: #f8f9fa;
        }}
      </style>
    </head>
    <body>
      <div id="mynetwork"></div>
      <script>
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        var options = {{
          nodes: {{
            shape: "box",
            font: {{ size: 14 }},
            color: {{
              background: "#4285F4",
              border: "#2B6CDE",
              highlight: {{ background: "#34A853", border: "#2B8D4A" }},
            }},
            shadow: true
          }},
          edges: {{
            arrows: "to",
            smooth: true,
            font: {{ size: 12, color: "#666" }},
            color: {{ color: "#666", highlight: "#34A853" }}
          }},
          layout: {{
            hierarchical: {{
              enabled: true,
              direction: "UD",
              levelSeparation: 120,
              nodeSpacing: 100
            }}
          }},
          physics: {{ stabilization: true }}
        }};
        new vis.Network(document.getElementById("mynetwork"), {{ nodes: nodes, edges: edges }}, options);
      </script>
    </body>
    </html>
    """
    st.subheader("🧠 Course Mind Map")
    st.components.v1.html(html, height=550)

# --- Generate Customized Course ---
def generate_custom_course(content, user_summary, api_key, llm_model):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model)

    prompt = f"""Customize this course content for the following user profile:
    {user_summary}
    
    Content:
    {content}"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Course generation failed: {str(e)}")
        return ""

# --- Streamlit UI ---
st.set_page_config(page_title="AI Course Generator", layout="wide")

st.title("📘 AI-Powered Custom Course Generator")

st.markdown("Upload a course PDF or paste raw content below. Customize it for a user profile and generate an interactive mind map using Gemini AI.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📂 Upload Course PDF", type=["pdf"])
#with col2:
#    raw_text = st.text_area("Or paste raw course content:", height=150)

st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    llm_model = st.selectbox(
        'Gemini Model',
        ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest']
    )
    api_key = st.text_input('🔐 Gemini API Key', type="password")
    st.markdown("---")
    st.markdown("🧑💻 User Profile")
    user_summary = st.text_area(
        "User Summary",
        height=150,
        value="John Doe, 4 years management experience, plant head level"
    )

# Process
if st.button("🚀 Generate Course"):
    if not api_key:
        st.warning("Please enter your Gemini API Key.")
    else:
        if uploaded_file:
            pdf_content = read_pdf(uploaded_file)
        elif raw_text.strip():
            pdf_content = raw_text.strip()
        else:
            st.warning("Please upload a PDF or paste course content.")
            st.stop()

        with st.spinner("🔍 Generating personalized course..."):
            custom_course = generate_custom_course(pdf_content, user_summary, api_key, llm_model)

        if custom_course:
            st.subheader("📚 Customized Course Content")
            st.markdown(custom_course)

            st.download_button("⬇️ Download Course", custom_course, file_name="custom_course.md")

            with st.spinner("🧠 Generating mind map..."):
                mindmap_data = generate_mindmap_data(custom_course, api_key, llm_model)
                visualize_mindmap(mindmap_data)

                if mindmap_data:
                    st.download_button("⬇️ Download Mind Map JSON", json.dumps(mindmap_data, indent=2), file_name="mindmap.json")
