# AI Mock Interview & Performance Analyzer

A polished, local-first Flask web application for B.Tech CSE students and early-career candidates to practice interviews, receive answer-sensitive AI-style feedback, and follow a personalized preparation plan.

## Problem Statement

Students often prepare with generic question lists but do not get a realistic practice loop or useful feedback on clarity, technical depth, relevance, and completeness.

## Objective

Provide a private, no-database interview workspace that turns a selected role and experience level into realistic practice questions, structured evaluation, a performance report, and a seven-day improvement plan.

## Features

- Premium responsive landing page with Home, How It Works, and About navigation
- Setup for name, target role, experience, interview type, and 5, 10, or 15 questions
- Role-specific question bank for Data Analyst, Software Developer, Python Developer, Java Developer, Web Developer, Business Analyst, HR, and General interviews
- Per-question timer, progress bar, previous question, skip question, and answer submission
- Local answer evaluator that responds to answer length, topic coverage, structure, examples, confidence language, and sentence clarity
- Feedback panel with score, relevance, technical knowledge, clarity, completeness, communication, strengths, missing points, improved answer, and interviewer tip
- Final performance report with overall score out of 100, category dashboard, question-level performance, strengths, weaknesses, and feedback
- Dynamic seven-day preparation plan based on weak score categories and target role
- Printable/downloadable report view through the browser print dialog
- Flask session storage only; no database or paid API required
- Friendly validation and error handling for empty answers, invalid setup, refreshes, and missing sessions

## Technology Stack

Python, Flask, Jinja2, HTML, CSS, JavaScript, `python-dotenv`, and Flask signed sessions. The default application does not import or require Gemini/OpenAI. A real provider can be added later behind the evaluator interface if desired.

## Project Architecture

```text
AI-Mock-Interview/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── setup.html
│   ├── interview.html
│   ├── feedback.html
│   ├── report.html
│   └── preparation.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## How It Works

1. The candidate chooses a role and session format.
2. Flask builds a question set from the local role-specific bank and stores it in the signed session.
3. Each submitted answer is evaluated locally using measurable signals: length, topic overlap, examples, structure, confidence language, and sentence clarity.
4. The session aggregates each evaluation into a report and identifies categories below the improvement threshold.
5. Those weak areas become the focus of a dynamic seven-day preparation plan.

## Installation

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, use the virtual environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuration

The application works without a paid API key. `.env` may contain `FLASK_SECRET_KEY` for session signing. Never commit real credentials; `.env` is ignored by Git. `GEMINI_API_KEY` is not read or needed by the current local engine.

## How To Run

```powershell
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000.

## Screenshots

_Add screenshots of the landing page, interview feedback panel, and final report here._

## Future Enhancements

- Optional provider adapter for Gemini or another model
- Voice answers and transcription
- Export to a generated PDF file
- Persistent history with an opt-in local database
- Authentication and shareable preparation plans
- Automated browser test coverage and deployment configuration
