# Detailed documentation of Visa chatbot web application

**Architecture Diagram**
User Query->Streamlit UI
Streamlit->Gemini 2.5-Flash (with Search Tool enabled)
Gemini->Google Search Grounding (Retrieval).
Augmented Response->User.

**Project Overview**
Visa Helper is a web application designed for solving the queries of users who face common issues in applying for a visa. With its **HTML+CSS+FlaskAPI** frontend and a **Python** backend, it responds with verified referrals from the internet, assisting users efficiently.
Consisting of user-friendly interface and minimal colour combination (blue and white), Visa Helper is deployed on streamlit and open to the audience exploring the various different methodologies for visas, their importance, procedures, and a ready-to-refer list of websites for further information.

**File**
This project consists of:
a) README.md (a detailed overview of this project)
b) .gitignore (important for ignoring .env file, which contains secrets/credentials)
c) app.py (the main program code)
d) .env (secrets)
e) requirements.txt (the necessary libraries and imports)

**Development**
I developed this application to address the concerns of users struggling with incomplete, redundant and outdated visa information found on most of the applications or websites, which are not updated regularly.
Visa helper explores up-to-date and accurate information regarding visa, using RAG (Retrieval Augmented Generation) technique, which extracts information sourced from valid or official websites instead and helps users solve almost every visa problem users face in day-to-day lives. 
I used python, Google Gemini, Windows Command Prompt and Windows Powershell for developing this application and deploying it on streamlit.

**Challenges faced**
I faced challenges like:
a) 403 error, model not found: I accidentally used an older model, gemini-1.5-flash in my code which caused the application to crash. I corrected it by changing the model name to gemini-2.5-flash.
b) The "send" button was not working due to a variable name mismatch and coding glitch, I corrected it with the duly assistance of Google Gemini.
c) 429 Quota exhausted error: While implementing RAG using custom search engine, my API key quota was exhausted, and then I switched to google-genai SDK which helps this application retrieve information from the web using Gemini itself, removing the quota problem altogether.
