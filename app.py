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

# --- 2. PASTEL THEME CSS ---
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --bg:          #f5f0eb;
    --surface:     #fffaf6;
    --sidebar-bg:  #fdf3e7;
    --accent1:     #e8c5a0;   /* warm peach */
    --accent2:     #b5c9e8;   /* soft sky blue */
    --accent3:     #c9e8c5;   /* mint */
    --accent4:     #e8c5d6;   /* blush pink */
    --text-dark:   #3a3028;
    --text-mid:    #6b5c4e;
    --text-light:  #9e8e80;
    --bubble-user: #ddeaff;   /* user bubble: periwinkle */
    --bubble-ai:   #fff4e6;   /* AI bubble: warm cream */
    --border:      #e5d9ce;
    --shadow:      rgba(100, 70, 40, 0.08);
}

/* ── App background ── */
.stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-dark);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1.5px solid var(--border);
}
[data-testid="stSidebar"] .stButton > button {
    background: var(--accent1);
    color: var(--text-dark);
    border: none;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    padding: 0.55rem 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px var(--shadow);
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #d4a87a;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow);
}
[data-testid="stSidebar"] .stDownloadButton > button {
    background: var(--accent2) !important;
    color: var(--text-dark) !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px var(--shadow);
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: #94b3d6 !important;
    transform: translateY(-1px);
}

/* ── Main title ── */
h1 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--text-dark) !important;
    letter-spacing: -0.5px;
}
h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--text-mid) !important;
}

/* ── Chat area background ── */
[data-testid="stChatMessageContainer"] {
    background: transparent !important;
}

/* ── USER chat bubble ── */
[data-testid="stChatMessage"][data-testid*="user"],
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--bubble-user) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 14px 18px !important;
    margin: 8px 0 8px 15% !important;
    border: 1.5px solid #c2d4f5 !important;
    box-shadow: 0 2px 10px rgba(100, 140, 200, 0.12) !important;
}

/* ── ASSISTANT chat bubble ── */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: var(--bubble-ai) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 14px 18px !important;
    margin: 8px 15% 8px 0 !important;
    border: 1.5px solid #f0dcc5 !important;
    box-shadow: 0 2px 10px rgba(180, 120, 60, 0.10) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border-radius: 16px !important;
    border: 2px solid var(--accent1) !important;
    box-shadow: 0 2px 12px var(--shadow);
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #b08060 !important;
    box-shadow: 0 4px 18px rgba(160,100,50,0.15) !important;
}

/* ── Expander (sources) ── */
[data-testid="stExpander"] {
    background: #fef9f4 !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text-mid) !important;
}

/* ── Info / Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-mid);
    font-size: 0.9rem;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--accent1) !important;
}

/* ── Tag pill for sidebar title ── */
.sidebar-pill {
    display: inline-block;
    background: var(--accent4);
    color: var(--text-dark);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 6px;
}

/* ── Welcome card ── */
.welcome-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px var(--shadow);
    text-align: center;
}
.welcome-card h2 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.5rem;
    color: var(--text-dark) !important;
    margin-bottom: 8px;
}
.welcome-card p {
    color: var(--text-mid);
    font-size: 0.95rem;
    margin: 0;
}
.badge-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 16px;
}
.badge {
    background: var(--accent3);
    color: var(--text-dark);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 500;
}

/* ── Source link styling ── */
.source-link {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    color: #5a7fbf;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZE CLIENT ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "checklist" not in st.session_state:
    st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]

# --- 5. HELPER FUNCTIONS ---
def generate_summary(history):
    if not history:
        return "No conversation history to summarize."
    summary_prompt = "Summarize the visa consultation above into a concise, professional one-paragraph travel plan."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history + [types.Content(role="user", parts=[types.Part.from_text(text=summary_prompt)])]
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
    """Safely extract grounding metadata from a Gemini response."""
    try:
        candidates = response.candidates
        if not candidates:
            return None, None, None

        candidate = candidates[0]
        metadata = getattr(candidate, "grounding_metadata", None)
        if metadata is None:
            return None, None, None

        search_entry_point = getattr(metadata, "search_entry_point", None)
        grounding_chunks = getattr(metadata, "grounding_chunks", None) or []
        grounding_supports = getattr(metadata, "grounding_supports", None) or []

        return search_entry_point, grounding_chunks, grounding_supports
    except Exception:
        return None, None, None

# --- 6. SIDEBAR UI ---
with st.sidebar:
    st.markdown('<div class="sidebar-pill">🌐 AI-Powered</div>', unsafe_allow_html=True)
    st.title("Visa Helper")
    st.info("💡 Powered by real-time Google Search for accurate, up-to-date visa information.")

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
        summary = generate_summary(st.session_state.history)
        st.info(summary)

    if st.button("🔄 Start New Consultation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.checklist = ["Passport (Valid 6+ months)", "Recent Photograph"]
        st.rerun()

# --- 7. MAIN CHAT UI ---
st.title("🌎 Visa Helper AI")
st.markdown("---")

# Welcome card (shown only when no messages)
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h2>Your Personal Visa Consultant</h2>
        <p>Ask anything about visa requirements, documents, processing times, and application tips — powered by live Google Search.</p>
        <div class="badge-row">
            <span class="badge">✈️ Tourist Visas</span>
            <span class="badge">💼 Work Permits</span>
            <span class="badge">🎓 Student Visas</span>
            <span class="badge">👨‍👩‍👧 Family Reunion</span>
            <span class="badge">🏠 Residency</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT INPUT & RESPONSE ---
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

            # Extract checklist items from [brackets]
            new_docs = re.findall(r"\[([^\[\]]+)\]", ai_response)
            for doc in new_docs:
                if doc not in st.session_state.checklist:
                    st.session_state.checklist.append(doc)

            # Clean brackets for display
            final_display = ai_response.replace("[", "").replace("]", "")

            # Extract grounding metadata safely
            search_entry_point, grounding_chunks, _ = safe_get_grounding(response)

        # Render assistant response
        with st.chat_message("assistant"):
            st.markdown(final_display)

            # ── Google Search suggestion widget ──
            if search_entry_point:
                rendered = getattr(search_entry_point, "rendered_content", None)
                if rendered:
                    st.markdown("---")
                    st.components.v1.html(rendered, height=80, scrolling=False)

            # ── Source links in expander ──
            if grounding_chunks:
                seen_uris = set()
                valid_sources = []
                for chunk in grounding_chunks:
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
