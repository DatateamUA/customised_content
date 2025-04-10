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
    try:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            parsed = json.loads(json_match.group())
            if "nodes" in parsed and "edges" in parsed:
                return parsed
    except json.JSONDecodeError as e:
        st.error(f"⚠️ JSON decode error: {e}")
    raise ValueError("Gemini returned no valid JSON.")

# --- Generate Mind Map JSON ---
def generate_mindmap_data(content, api_key, model_name):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    prompt = f"""Convert the following course module into a JSON-based mind map.
Return ONLY valid JSON with two keys:
- "nodes": List of objects like {{"id": "unique_id", "label": "Node Label", "group": "Module/Subtopic"}}
- "edges": List of objects like {{"from": "parent_id", "to": "child_id", "label": "relationship"}}

Ensure:
- IDs are unique
- Use short, clear labels
- Connect related concepts logically

Content: {content[:2800]}"""

    try:
        response = model.generate_content(prompt)
        return extract_json_from_response(response.text)
    except Exception as e:
        st.error(f"❌ Mindmap generation failed: {str(e)}")
        return None

# --- Visualize Mind Map ---
def visualize_mindmap(data, title="🧠 Module Mind Map"):
    if not data or "nodes" not in data or "edges" not in data:
        st.warning("⚠️ Invalid mindmap data.")
        return

    nodes = [{"id": n["id"], "label": n["label"], "group": n.get("group", "default")} for n in data["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in data["edges"]]

    st.caption(f"🧩 Total Nodes: {len(nodes)} | 🔗 Total Edges: {len(edges)}")

    html = f"""
    <html>
    <head>
      <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
      <style>
        #mynetwork {{
          width: 100%;
          height: 600px;
          border: 2px solid #ddd;
          background: #f7f9fc;
          border-radius: 8px;
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
            font: {{ size: 14, face: 'monospace' }},
            margin: 10,
            color: {{
              background: "#e3f2fd",
              border: "#90caf9",
              highlight: {{
                background: "#bbdefb",
                border: "#1976d2"
              }}
            }},
            shadow: true
          }},
          edges: {{
            arrows: "to",
            smooth: {{ type: "cubicBezier", forceDirection: "vertical", roundness: 0.4 }},
            font: {{ size: 12, color: "#333" }},
            color: {{ color: "#90a4ae", highlight: "#1976d2" }}
          }},
          layout: {{
            hierarchical: {{
              enabled: true,
              direction: "UD",
              levelSeparation: 140,
              nodeSpacing: 150,
              treeSpacing: 200
            }}
          }},
          physics: false
        }};
        new vis.Network(document.getElementById("mynetwork"), {{ nodes: nodes, edges: edges }}, options);
      </script>
    </body>
    </html>
    """
    st.subheader(title)
    st.components.v1.html(html, height=630)

# --- Generate Customized Course ---
def generate_custom_course(content, user_summary, api_key, llm_model):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model)

    prompt = f"""Customize the following course content to align with the individual's specific needs, challenges, and professional goals. Ensure that the material is highly relevant, practical, and engaging for their role.
At the beginning, include a concise summary that highlights the key takeaways and benefits tailored for the individual based on the provided context.

User Information:
{user_summary}

Course Content:
{content}"""

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
st.set_page_config(page_title="AI Course Generator", layout="wide")

st.title("📘 AI-Powered Custom Course Generator")
st.markdown("Upload a course PDF and customize it for a user profile. Visualize each module as a mind map and get a final summary.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📂 Upload Course PDF", type=["pdf"])

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    llm_model = st.selectbox('Gemini Model', [ 'gemini-1.5-flash-latest','gemini-1.5-pro-latest'])
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

        modules = split_into_modules(custom_course)
        st.markdown("---")
        st.header("🧩 Module-wise Mind Maps")

        for idx, module in enumerate(modules, start=1):
            with st.spinner(f"🔧 Generating Mind Map for Module {idx}..."):
                mindmap_data = generate_mindmap_data(module, api_key, llm_model)
                visualize_mindmap(mindmap_data, title=f"🧠 Mind Map - Module {idx}")
                if mindmap_data:
                    st.download_button(
                        f"⬇️ Download Mind Map {idx} JSON",
                        json.dumps(mindmap_data, indent=2),
                        file_name=f"mindmap_module_{idx}.json"
                    )

        st.markdown("---")
        st.header("📌 Course Summary")
        with st.spinner("🧾 Generating summary..."):
            summary = generate_summary(custom_course, api_key, llm_model)
            st.markdown(summary)
