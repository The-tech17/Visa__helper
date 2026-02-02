## 🌎 Project Documentation: Visa Helper AI Support

### 1. Architecture Overview

The application follows a **RAG (Retrieval-Augmented Generation)** pattern, ensuring that responses are grounded in real-time, authoritative data rather than just static training knowledge.

* **User Layer:** A responsive Streamlit interface for seamless query input.
* **Orchestration Layer:** A Python backend (google-genai SDK) that coordinates between the user and the AI.
* **Intelligence & Retrieval Layer:** **Gemini 2.5 Flash** integrated with the **Google Search Tool**, which automatically triggers web searches to retrieve and synthesize current visa regulations and official links.

### 2. Project Vision & Purpose

**Visa Helper** addresses a critical gap in the immigration space: the prevalence of outdated or redundant visa information. Many official processes change monthly, and static websites often fail to keep pace.

By leveraging real-time search grounding, this application solves the "hallucination" problem common in standard LLMs. It assists users in exploring visa methodologies, importance, and specific procedures while providing a ready-to-refer list of official government websites.

### 3. Technical Stack

| Category | Technology |
| --- | --- |
| **Language** | Python 3.10+ |
| **Framework** | Streamlit |
| **AI Model** | Google Gemini 2.5 Flash |
| **SDK/API** | google-genai (Search Grounding Tool) |
| **Tools** | Windows PowerShell, GitHub, Dotenv |

### 4. File Structure

* **`app.py`**: The core logic containing the Streamlit UI and Gemini API orchestration.
* **`requirements.txt`**: Defined dependencies to ensure environment reproducibility.
* **`.env`**: Secure storage for API credentials (excluded from version control).
* **`.gitignore`**: Critical for protecting sensitive keys and ignoring Python cache files.
* **`README.md`**: High-level project summary and setup instructions.

### 5. Challenges & Engineering Solutions

One of the most valuable parts of this project was the iterative debugging process:

* **The Model Version Pivot:** Initially, a `403 Permission Denied` error occurred due to using restricted experimental model strings. I solved this by standardizing on **Gemini 2.5 Flash**, which offers the best balance of speed and RAG performance on the free tier.
* **Interface Optimization:** Debugged a "Send" button failure caused by a JavaScript variable mismatch in the early Flask prototype. I improved this by migrating the entire project to **Streamlit**, which eliminated the need for complex custom JS and simplified the state management.
* **API Quota Management:** Encountered a `429 Resource Exhausted` error while using a Custom Search API. I engineered a more robust solution by switching to the **native google-genai SDK Search Tool**, which integrates search directly into the model’s reasoning cycle, significantly reducing quota overhead and latency.
