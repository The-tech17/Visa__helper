import os
import re
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

# --- 1. PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="Visa Helper AI", page_icon="🌎", layout="wide")

# --- 2. THEME INITIALIZATION & SIDEBAR TOGGLE ---
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.sidebar:
    st.markdown('<div class="sidebar-pill">🎨 Appearance</div>', unsafe_allow_html=True)
    # The toggle updates the session state immediately
    dark_mode = st.toggle("Dark Mode", value=(st.session_state.theme == "Dark"))
    st.session_state.theme = "Dark" if dark_mode else "Light"

# --- 3. DYNAMIC CSS (Switches based on Toggle) ---
common_styles = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
.stApp { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
/* ... (Keep your existing bubble and button transition styles here) ... */
</style>
"""

if st.session_state.theme == "Light":
    theme_css = """
    <style>
    :root {
        --bg: #f5f0eb; --surface: #fffaf6; --sidebar-bg: #fdf3e7;
        --accent1: #e8c5a0; --accent2: #b5c9e8; --accent3: #c9e8c5; --accent4: #e8c5d6;
        --text-dark: #3a3028; --text-mid: #6b5c4e;
        --bubble-user: #ddeaff; --bubble-ai: #fff4e6; --border: #e5d9ce;
    }
    .stApp { background-color: var(--bg) !important; color: var(--text-dark); }
    [data-testid="stSidebar"] { background-color: var(--sidebar-bg) !important; }
    </style>
    """
else:
    theme_css = """
    <style>
    :root {
        --bg: #0f111a; --surface: #1a1d2b; --sidebar-bg: #121420;
        --accent1: #82aaff; --accent2: #c792ea; --accent3: #c3e88d; --accent4: #ff757f;
        --text-dark: #ffffff; --text-mid: #a6accd;
        --bubble-user: #2d324d; --bubble-ai: #232635; --border: #2d324d;
    }
    .stApp { background-color: var(--bg) !important; color: var(--text-dark) !important; }
    [data-testid="stSidebar"] { background-color: var(--sidebar-bg) !important; }
    h1, h2, h3, p, span, label { color: var(--text-dark) !important; }
    </style>
    """

st.markdown(common_styles + theme_css, unsafe_allow_html=True)

# --- 4. INITIALIZE CLIENT ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- 5. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "checklist" not in st.session_state:
    st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]

# --- 6. HELPER FUNCTIONS ---
def generate_summary(history):
    if not history: return "No conversation history to summarize."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history + [types.Content(role="user", parts=[types.Part.from_text(text="Summarize this consultation in one paragraph.")])]
        )
        return response.text
    except Exception as e:
        return f"Summary snag: {str(e)}"

def generate_pdf(items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Visa Document Checklist", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    for item in items:
        pdf.cell(0, 10, f"[ ] {item}", ln=True)
    return bytes(pdf.output())

def safe_get_grounding(response):
    try:
        metadata = response.candidates[0].grounding_metadata
        return metadata.search_entry_point, metadata.grounding_chunks or []
    except:
        return None, []

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("Visa Helper")
    st.info("💡 Real-time Google Search powered.")
    st.markdown("### 📋 Your Visa Roadmap")
    for item in st.session_state.checklist:
        st.checkbox(item, key=f"check_{item}")
    
    if st.session_state.checklist:
        st.download_button("📄 Download PDF", data=generate_pdf(st.session_state.checklist), file_name="visa_checklist.pdf")
    
    if st.button("📝 Summarize Consultation", use_container_width=True):
        st.info(generate_summary(st.session_state.history))

    if st.button("🔄 Start New Consultation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]
        st.rerun()

# --- 8. MAIN CHAT ---
st.title("🌎 Visa Helper AI")

if not st.session_state.messages:
    st.markdown('<div class="welcome-card"><h2>Your Personal Visa Consultant</h2><p>Ask about requirements, documents, and tips.</p></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your visa..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

    try:
        with st.spinner("Searching official sources..."):
            config = types.GenerateContentConfig(
                system_instruction="Professional Visa Assistant. Use [brackets] for documents.",
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
            response = client.models.generate_content(model="gemini-2.5-flash", contents=st.session_state.history, config=config)
            
            ai_response = response.text or ""
            st.session_state.history.append(types.Content(role="model", parts=[types.Part.from_text(text=ai_response)]))

            # Update Checklist
            new_docs = re.findall(r"\[([^\[\]]+)\]", ai_response)
            for doc in new_docs:
                if doc not in st.session_state.checklist:
                    st.session_state.checklist.append(doc)

            final_display = ai_response.replace("[", "").replace("]", "")
            search_entry, chunks = safe_get_grounding(response)

        with st.chat_message("assistant"):
            st.markdown(final_display)
            if search_entry and hasattr(search_entry, 'rendered_content'):
                st.components.v1.html(search_entry.rendered_content, height=80)
            
            if chunks:
                with st.expander(f"🔍 View Sources"):
                    seen = set()
                    for c in chunks:
                        if hasattr(c, 'web') and c.web.uri not in seen:
                            st.markdown(f"🔗 [{c.web.title or 'Source'}]({c.web.uri})")
                            seen.add(c.web.uri)

        st.session_state.messages.append({"role": "assistant", "content": final_display})
        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
