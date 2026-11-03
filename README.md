# 🤖 VMC Chatbot — Backend

The API layer of the VMC Chatbot: a **FastAPI** service that handles authentication, data storage and AI-powered responses using **Google Gemini** and **OpenAI**.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)

> 🔗 **Frontend repository:** [vmc-chatbot-frontend](https://github.com/saintcoder0/vmc-chatbot-frontend)

---

## ✨ Features

- **AI responses** powered by Google Gemini (`google-generativeai`) and the OpenAI API
- **Language detection** with `langdetect` to understand the language of incoming queries
- **Secure authentication** using JWT tokens (`python-jose`) and bcrypt-hashed passwords (`passlib`)
- **Relational data layer** built with SQLModel and SQLAlchemy
- **Validated requests and responses** through Pydantic models and settings management
- **PDF generation** with ReportLab
- **File and image uploads** via `python-multipart` and Pillow
- **Tested** with Pytest

> 🔧 *Add your specifics here:* what the chatbot answers, who uses it, and the main endpoints.

---

## 🛠 Tech Stack

| Area            | Tools                                      |
|-----------------|--------------------------------------------|
| Framework       | FastAPI, Uvicorn                           |
| AI / LLM        | Google Generative AI (Gemini), OpenAI      |
| Database / ORM  | SQLModel, SQLAlchemy                       |
| Auth & Security | python-jose (JWT), passlib, bcrypt         |
| Validation      | Pydantic, pydantic-settings                |
| Utilities       | langdetect, ReportLab, Pillow, httpx       |
| Testing         | Pytest                                     |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/saintcoder0/vmc-chatbot-backend.git
cd vmc-chatbot-backend
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root (adjust names to match your code):

```env
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_jwt_secret
DATABASE_URL=your_database_url
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

*(Adjust `main:app` to your actual module path.)*

The interactive API docs are available at **http://localhost:8000/docs**.

---

## 🧪 Running Tests

```bash
pytest
```

---

## 👤 Author

**Tushar Sharma**
[GitHub](https://github.com/saintcoder0) · [LinkedIn](https://www.linkedin.com/in/tushar-sharma-83b10a270/)
