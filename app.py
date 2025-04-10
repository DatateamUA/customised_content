import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import re
import textwrap

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

    prompt = f"""Convert the following content into a mindmap structure. Return ONLY valid JSON with:
    - \"nodes\" (list of {{\"id\", \"label\", \"group\"}})
    - \"edges\" (list of {{\"from\", \"to\", \"label\"}})

    Content: {content[:3000]}"""

    try:
        response = model.generate_content(prompt)
        return extract_json_from_response(response.text)
    except Exception as e:
        st.error(f"❌ Mindmap generation failed: {str(e)}")
        return None

# --- Visualize Mind Map ---
def visualize_mindmap(data, title="🧠 Mind Map"):
    if not data or "nodes" not in data:
        st.warning("⚠️ Invalid mindmap data.")
        return

    nodes = [{"id": n["id"], "label": n["label"], "group": n.get("group", "default")} for n in data["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in data["edges"]]

    html = f"""
    <html>
    <head>
      <script src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
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
      <div id=\"mynetwork\"></div>
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
    st.subheader(title)
    st.components.v1.html(html, height=550)

# --- Generate Customized Course ---
def generate_custom_course(content, user_summary, api_key, llm_model):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model)

    prompt = f'''Customize the following course content to align with the individual's specific needs, challenges, and professional goals. Ensure that the material is highly relevant, practical, and engaging for their role.
At the beginning, include a concise summary that highlights the key takeaways and benefits tailored for the individual based on the provided context.

User Information:
{user_summary}

Course Content:
{content}'''

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Course generation failed: {str(e)}")
        return ""

# --- Split text into chunks (~1500 words each) ---
def split_text(text, words_per_chunk=1500):
    words = text.split()
    return [" ".join(words[i:i+words_per_chunk]) for i in range(0, len(words), words_per_chunk)]

# --- Generate Summary ---
def generate_summary(text, api_key, model_name):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    prompt = f"""Summarize the following course in a structured format, listing key topics and outcomes clearly:

    {text[:5000]}"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Summary generation failed: {str(e)}")
        return ""

# --- Streamlit UI ---
st.set_page_config(page_title="AI Course Generator", layout="wide")
st.title("📘 AI-Powered Modular Course Builder")

st.markdown("Upload a course PDF, generate a customized course per user, visualize each module with a mind map, and get a final summary.")

uploaded_file = st.file_uploader("📂 Upload Course PDF", type=["pdf"])

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    llm_model = st.selectbox('Gemini Model', ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest'])
    api_key = st.text_input('🔐 Gemini API Key', type="password")
    st.markdown("---")
    user_summary = st.text_area("👤 User Profile", value="John Doe, 4 years management experience, plant head level", height=150)

# Main Trigger
if st.button("🚀 Build Modular Course"):
    if not api_key:
        st.warning("Please provide a Gemini API Key.")
        st.stop()

    if not uploaded_file:
        st.warning("Please upload a PDF file.")
        st.stop()

    with st.spinner("📖 Reading PDF..."):
        pdf_content = read_pdf(uploaded_file)

    with st.spinner("🛠️ Customizing Course..."):
        custom_course = generate_custom_course(pdf_content, user_summary, api_key, llm_model)

    # Split course into logical chunks
    modules = split_text(custom_course, words_per_chunk=1500)

    st.header("📚 Modular Course with Mind Maps")

    for i, module in enumerate(modules, start=1):
        st.markdown(f"### 📦 Module {i}")
        st.markdown(module)

        with st.spinner(f"🧠 Generating mind map for Module {i}..."):
            mindmap = generate_mindmap_data(module, api_key, llm_model)
            visualize_mindmap(mindmap, title=f"🧠 Mind Map - Module {i}")

    st.markdown("---")
    st.header("📌 Final Course Summary")

    with st.spinner("📑 Summarizing full course..."):
        summary_text = generate_summary(custom_course, api_key, llm_model)
        st.markdown(summary_text)

    with st.spinner("🧠 Generating summary mind map..."):
        summary_mindmap = generate_mindmap_data(summary_text, api_key, llm_model)
        visualize_mindmap(summary_mindmap, title="🧠 Mind Map - Summary")
