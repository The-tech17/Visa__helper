🌎 Visa Helper: AI-Powered Immigration Assistant
Visa Helper is a conversational AI designed to provide up-to-date visa application guidance. By utilizing Retrieval-Augmented Generation (RAG), the assistant doesn't just rely on static knowledge; it performs real-time Google searches to fetch the latest requirements, forms, and official links for users worldwide.

🚀 Live Demo
Check out the live app on Streamlit Cloud here!

✨ Key Features
Real-Time Data Retrieval: Uses Google Search grounding to avoid outdated information.

Context-Aware Chat: Remembers your conversation history for a natural experience.

Official Sources: Automatically provides links to official consulate and government websites.

Modern UI: A clean, responsive interface built with Streamlit.

🛠️ Tech Stack
Core AI: Gemini 2.5 Flash (Google Generative AI)

Framework: Streamlit

RAG Engine: Google Search Grounding (via Google Gen AI SDK)

Environment Management: Python-Dotenv

Language: Python 3.10+

📂 Project Structure
Plaintext
Visa_helper/
├── app.py              # Main Streamlit application logic
├── requirements.txt    # Project dependencies
├── .env                # API Keys (Local use only)
└── .gitignore          # Prevents sensitive files from being uploaded

⚙️ Installation & Setup

Clone the repository:
git clone https://github.com/YOUR_USERNAME/Visa_helper.git
cd Visa_helper

Install dependencies:
pip install -r requirements.txt

Configure API Keys: Create a .env file in the root directory and add your key: GEMINI_API_KEY=your_actual_key_here

Run the app:
streamlit run app.py

🔒 Security Note
This project uses .gitignore to ensure that the .env file containing private API keys is never pushed to GitHub. When deploying to Streamlit Cloud, secrets are managed securely via the Streamlit Secrets manager.