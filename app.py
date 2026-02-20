import os
import re
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

# ─────────────────────────────────────────────
# 1. PAGE CONFIG  (must be the very first st.* call)
# ─────────────────────────────────────────────
st.set_page_config(page_title="Visa Helper AI", page_icon="🌎", layout="wide")

# ─────────────────────────────────────────────
# 2. THEME SESSION STATE  (init before any widget)
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ─────────────────────────────────────────────
# 3. INJECT ALL CSS  (one single call, top-level only)
#    We read the theme flag that was set on the *previous* run.
#    The toggle below will flip it and trigger st.rerun().
# ─────────────────────────────────────────────
IS_DARK = (st.session_state.theme == "Dark")

LIGHT_VARS = """
    --bg:          #f5f0eb;
    --surface:     #fffaf6;
    --sidebar-bg:  #fdf3e7;
    --accent1:     #e8c5a0;
    --accent2:     #b5c9e8;
    --accent3:     #c9e8c5;
    --accent4:     #e8c5d6;
    --text-dark:   #3a3028;
    --text-mid:    #6b5c4e;
    --text-light:  #9e8e80;
    --bubble-user: #ddeaff;
    --bubble-ai:   #fff4e6;
    --border:      #e5d9ce;
    --shadow:      rgba(100,70,40,0.08);
    --input-border:#e8c5a0;
"""

DARK_VARS = """
    --bg:          #0f111a;
    --surface:     #1a1d2b;
    --sidebar-bg:  #121420;
    --accent1:     #82aaff;
    --accent2:     #7ec8b8;
    --accent3:     #a8d8a8;
    --accent4:     #d8a8c8;
    --text-dark:   #e8eaf0;
    --text-mid:    #b0b8d0;
    --text-light:  #7880a0;
    --bubble-user: #2d324d;
    --bubble-ai:   #232635;
    --border:      #2a2e42;
    --shadow:      rgba(0,0,0,0.3);
    --input-border:#82aaff;
"""

theme_vars = DARK_VARS if IS_DARK else LIGHT_VARS

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ── */
:root {{ {theme_vars} }}

/* ── Global ── */
.stApp {{
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-dark) !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1.5px solid var(--border);
}}

/* ── All text elements ── */
h1, h2, h3, h4, p, span, label, div,
.stMarkdown, .stText, [data-testid="stMarkdownContainer"] p {{
    color: var(--text-dark) !important;
}}
h1, h2, h3 {{
    font-family: 'DM Serif Display', serif !important;
}}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {{
    background: var(--accent1) !important;
    color: var(--text-dark) !important;
    border: none;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    padding: 0.55rem 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px var(--shadow);
    width: 100%;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    opacity: 0.85;
    transform: translateY(-1px);
}}
[data-testid="stSidebar"] .stDownloadButton > button {{
    background: var(--accent2) !important;
    color: var(--text-dark) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s ease;
}}

/* ── User chat bubble ── */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    background: var(--bubble-user) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 14px 18px !important;
    margin: 8px 0 8px 12% !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: 0 2px 10px var(--shadow) !important;
}}

/* ── Assistant chat bubble ── */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    background: var(--bubble-ai) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 14px 18px !important;
    margin: 8px 12% 8px 0 !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: 0 2px 10px var(--shadow) !important;
}}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {{
    background: var(--surface) !important;
    color: var(--text-dark) !important;
    border: 2px solid var(--input-border) !important;
    border-radius: 16px !important;
}}
[data-testid="stChatInput"] {{
    background: var(--surface) !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px var(--shadow);
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: var(--surface) !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
}}
[data-testid="stExpander"] summary {{
    color: var(--text-mid) !important;
    font-weight: 600 !important;
}}

/* ── Info / Alert boxes ── */
[data-testid="stAlert"] {{
    background: var(--surface) !important;
    border-radius: 12px !important;
    color: var(--text-dark) !important;
}}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {{
    color: var(--text-mid) !important;
    font-size: 0.9rem;
}}

/* ── Toggle switch label ── */
[data-testid="stToggle"] label {{
    color: var(--text-dark) !important;
    font-weight: 500;
}}

/* ── Divider ── */
hr {{ border-color: var(--border) !important; }}

/* ── Welcome card ── */
.welcome-card {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px var(--shadow);
    text-align: center;
}}
.welcome-card h2 {{
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.5rem;
    color: var(--text-dark) !important;
    margin-bottom: 8px;
}}
.welcome-card p {{
    color: var(--text-mid) !important;
    font-size: 0.95rem;
    margin: 0;
}}
.badge-row {{
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 16px;
}}
.badge {{
    background: var(--accent3);
    color: var(--text-dark) !important;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 500;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. INITIALIZE CLIENT
# ─────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ─────────────────────────────────────────────
# 5. SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "checklist" not in st.session_state:
    st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]

# ─────────────────────────────────────────────
# 6. HELPER FUNCTIONS
# ─────────────────────────────────────────────
def generate_summary(history):
    if not history:
        return "No conversation history to summarize."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history + [
                types.Content(role="user", parts=[types.Part.from_text(
                    text="Summarize this visa consultation in one concise paragraph."
                )])
            ]
        )
        return response.text
    except Exception as e:
        return f"Summary failed: {str(e)}"


def generate_pdf(items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Visa Application Document Checklist", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Personalized roadmap based on your AI consultation:", ln=True)
    pdf.ln(5)
    for item in items:
        pdf.cell(0, 10, f"[ ] {item}", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, "Generated by Visa Helper AI Support", ln=True, align="C")
    return bytes(pdf.output())


def safe_get_grounding(response):
    """Safely extract grounding metadata; returns (search_entry_point, chunks)."""
    try:
        if not response.candidates:
            return None, []
        metadata = getattr(response.candidates[0], "grounding_metadata", None)
        if metadata is None:
            return None, []
        entry = getattr(metadata, "search_entry_point", None)
        chunks = getattr(metadata, "grounding_chunks", None) or []
        return entry, chunks
    except Exception:
        return None, []

# ─────────────────────────────────────────────
# 7. SIDEBAR  (pure Streamlit widgets only — no st.markdown HTML here)
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("Visa Helper")
    st.info("💡 Powered by real-time Google Search.")

    # ── Dark mode toggle ──
    # Reads IS_DARK computed from session state at the top of the script.
    # When the user flips it, session state is updated and st.rerun() fires,
    # causing the CSS block (step 3) to re-render with the correct variables.
    st.markdown("### 🎨 Appearance")
    toggled = st.toggle("Dark Mode", value=IS_DARK, key="dark_mode_toggle")
    if toggled != IS_DARK:
        st.session_state.theme = "Dark" if toggled else "Light"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Your Visa Roadmap")
    for item in st.session_state.checklist:
        st.checkbox(item, key=f"check_{item}")

    if st.session_state.checklist:
        st.download_button(
            label="📄 Download Checklist (PDF)",
            data=generate_pdf(st.session_state.checklist),
            file_name="visa_checklist.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("---")

    if st.button("📝 Summarize Consultation", use_container_width=True):
        st.info(generate_summary(st.session_state.history))

    if st.button("🔄 Start New Consultation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]
        st.rerun()

# ─────────────────────────────────────────────
# 8. MAIN CHAT UI
# ─────────────────────────────────────────────
st.title("🌎 Visa Helper AI")
st.markdown("---")

# Welcome card (only when chat is empty)
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h2>Your Personal Visa Consultant</h2>
        <p>Ask anything about visa requirements, documents, processing times,
           and application tips — powered by live Google Search.</p>
        <div class="badge-row">
            <span class="badge">✈️ Tourist Visas</span>
            <span class="badge">💼 Work Permits</span>
            <span class="badge">🎓 Student Visas</span>
            <span class="badge">👨‍👩‍👧 Family Reunion</span>
            <span class="badge">🏠 Residency</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────────
# 9. CHAT INPUT & GEMINI CALL
# ─────────────────────────────────────────────
if prompt := st.chat_input("Ask about your visa application..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )

    try:
        with st.spinner("Searching official visa sources..."):
            config = types.GenerateContentConfig(
                system_instruction=(
                    "You are a professional Visa Assistant. "
                    "Always enclose required documents in [brackets] like [Work ID]. "
                    "Be clear, concise, and helpful."
                ),
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=st.session_state.history,
                config=config
            )

        ai_response = response.text or ""
        st.session_state.history.append(
            types.Content(role="model", parts=[types.Part.from_text(text=ai_response)])
        )

        # Extract document names for the checklist
        new_docs = re.findall(r"\[([^\[\]]+)\]", ai_response)
        for doc in new_docs:
            if doc not in st.session_state.checklist:
                st.session_state.checklist.append(doc)

        # Clean brackets for display
        final_display = ai_response.replace("[", "").replace("]", "")

        # Extract grounding data
        search_entry, chunks = safe_get_grounding(response)

        # Render assistant bubble
        with st.chat_message("assistant"):
            st.markdown(final_display)

            # Google "Search suggestions" widget
            if search_entry:
                rendered = getattr(search_entry, "rendered_content", None)
                if rendered:
                    st.markdown("---")
                    st.components.v1.html(rendered, height=80, scrolling=False)

            # Source links
            if chunks:
                seen_uris = set()
                valid_sources = []
                for chunk in chunks:
                    web = getattr(chunk, "web", None)
                    if web:
                        uri = getattr(web, "uri", None)
                        title = getattr(web, "title", None) or uri
                        if uri and uri not in seen_uris:
                            seen_uris.add(uri)
                            valid_sources.append((title, uri))

                if valid_sources:
                    with st.expander(f"🔍 View {len(valid_sources)} Official Source(s)"):
                        for title, uri in valid_sources:
                            st.markdown(f"🔗 [{title}]({uri})")

        st.session_state.messages.append({"role": "assistant", "content": final_display})
        st.rerun()

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
