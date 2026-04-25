# 🧠 Resume Analyzer

An AI-powered resume analyzer built with **LangGraph** and **Next.js**.

## What it does

- Extracts text from your uploaded resume PDF
- Analyzes strengths and weaknesses
- Compares your resume against a job description
- Decides if a rewrite is needed (conditional LangGraph branch)
- Rewrites your resume to better match the role
- Searches for live job listings matching the job description
- Saves all past analyses so you can revisit them

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| AI Pipeline | LangGraph (graph orchestration) |
| LLM | Groq — LLaMA 4 Scout |
| Job Search | Serper API |
| Database | SQLite via SQLAlchemy |

## How to run locally

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/resume-analyzer.git
cd resume-analyzer
```

### 2. Backend setup
```bash
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API keys: