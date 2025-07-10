
# 🧠 CV Review Assistant using Django + LangGraph ## (INCOMPLETE)

This project is an intelligent CV analysis tool built with **Django REST Framework**, **LangGraph**, and **Pydantic**. It allows users to upload a CV file, runs it through a document-reading agent and LangGraph pipeline, and returns a structured review with suggestions for improvement and relevant references.

---

## 📁 Project Structure

DjangoxAi/
├── main/
│ ├── app/
│ │ ├── views.py # Main logic for file handling and LangGraph invocation
│ │ ├── agents.py # LangGraph graph definition and node functions
│ │ └── ...
│ ├── settings.py # Django settings
│ └── urls.py # API routing
├── checkpoints/ # Directory for LangGraph checkpoints
├── templates/ # HTML templates (if used)
├── manage.py # Django CLI entry
├── requirements.txt # Dependencies


---

## 🚀 Features

- 📄 Upload CV documents (`.pdf`, `.docx`)
- 🧠 Automatically parses and reviews the CV
- 🔍 Adds search-based improvement references (e.g., via Tavily)
- 🧩 Modular LangGraph architecture with custom state and processing
- 🧾 Returns suggestions in a structured JSON format

---

## 🛠️ Setup Instructions

### 1. Create virtual environment
python -m venv venv
source venv/Scripts/activate
### 2. Install dependencies
pip install -r requirements.txt
### 3. Run the development server
python manage.py runserver
