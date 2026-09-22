import re
import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-demo-secret-change-me")

ROLES = ["Software Developer", "Data Analyst", "Data Scientist", "Web Developer", "Java Developer", "Python Developer", "Other"]
EXPERIENCE = ["Beginner", "Intermediate", "Advanced"]
INTERVIEW_TYPES = ["Technical", "HR / Behavioral", "Mixed"]
QUESTION_COUNTS = [5, 10]

QUESTION_BANK = {
    "Data Analyst": [("SQL", "How would you find the top three products by revenue for each region using SQL?"), ("Excel", "Describe how you would use Excel to investigate a sudden drop in sales."), ("Power BI", "How would you design a Power BI dashboard for a sales team?"), ("Data cleaning", "How do you handle missing, duplicate, and inconsistent data before analysis?"), ("Statistics", "Explain correlation versus causation with a business example."), ("Business scenario", "Conversion appears to drop, but the dashboard disagrees. How do you investigate?")],
    "Data Scientist": [("Statistics", "How would you choose an evaluation metric for a classification model?"), ("Python", "How would you use Python to prepare a dataset for a machine learning model?"), ("Machine learning", "Explain overfitting and two practical ways to reduce it."), ("SQL", "How would you use SQL to create features from customer transaction data?"), ("Experimentation", "How would you design an experiment to test a product recommendation?"), ("Communication", "How would you explain a model's result and limitations to a non-technical stakeholder?")],
    "Software Developer": [("Programming", "Explain a programming concept that helps you write maintainable code."), ("OOP", "What are the main principles of object-oriented design?"), ("DSA", "How would you choose a data structure for fast lookup and frequent updates?"), ("APIs", "How would you design and secure a REST API?"), ("Debugging", "How would you debug a production bug you cannot reproduce locally?"), ("Databases", "When would you choose a relational database over NoSQL?")],
    "Python Developer": [("Python", "What makes Python useful for application development?"), ("OOP", "Explain composition versus inheritance in Python."), ("DSA", "How would you find duplicate values efficiently in a large Python list?"), ("APIs", "How would you build a reliable Python API endpoint?"), ("Debugging", "How would you diagnose a slow Python function?"), ("Testing", "What would you test in a Python service before shipping?")],
    "Java Developer": [("Java", "Explain the difference between an interface and abstract class."), ("OOP", "How do encapsulation and polymorphism improve Java design?"), ("DSA", "How would you select a Java collection for unique searchable values?"), ("APIs", "What makes a Java REST service production-ready?"), ("Debugging", "How would you investigate a Java memory leak?"), ("Databases", "How do transactions and indexes affect a Java database layer?")],
    "Web Developer": [("HTML", "How would you make a form accessible and semantically correct?"), ("CSS", "When would you use Grid over Flexbox in responsive layouts?"), ("JavaScript", "Explain the JavaScript event loop."), ("Architecture", "What belongs in the frontend versus the backend?"), ("APIs", "How should a frontend handle API loading, errors, and retries?"), ("Performance", "How would you improve a web page with a poor performance score?")],
    "Business Analyst": [("Requirements", "How do you turn an ambiguous request into testable requirements?"), ("Stakeholders", "How would you resolve conflicting stakeholder priorities?"), ("SQL", "How can SQL validate a business recommendation?"), ("Business case", "How would you evaluate whether a feature is worth building?"), ("Analytics", "Which metrics show whether a process improvement worked?"), ("Delivery", "How do you keep requirements aligned during delivery?")],
    "HR": [("Introduction", "Tell me about yourself and what makes you a strong candidate."), ("Strengths", "What strength do you rely on in a team?"), ("Weaknesses", "What professional weakness are you actively improving?"), ("Teamwork", "Describe working with someone with a different style."), ("Conflict", "Tell me about a disagreement and how you handled it."), ("Leadership", "Describe a time you took ownership without being asked.")],
    "General": [("Introduction", "Walk me through your background and career choices."), ("Projects", "Tell me about a project you are proud of and what you learned."), ("Internships", "What was the most useful lesson from your practical experience?"), ("Teamwork", "Describe a team challenge and your role in solving it."), ("Problem solving", "Tell me about a difficult problem you solved."), ("Career goals", "What work do you want to grow into over the next few years?")],
    "Other": [("Introduction", "Walk me through your background and the role you want to grow into."), ("Projects", "Tell me about a project you are proud of and what you learned."), ("Problem solving", "Tell me about a difficult problem you solved and your approach."), ("Teamwork", "Describe a team challenge and how you contributed."), ("Communication", "How do you explain a complex idea to someone new to the topic?"), ("Career goals", "What work do you want to grow into over the next few years?")],
}


def guarded(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "interview" not in session:
            flash("Start a new interview before opening that page.", "error")
            return redirect(url_for("setup"))
        return view(*args, **kwargs)
    return wrapped


def make_questions(role, count, difficulty):
    bank = QUESTION_BANK.get(role, QUESTION_BANK["General"])
    questions = []
    for i in range(count):
        topic, text = bank[i % len(bank)]
        if difficulty == "Beginner":
            text = f"Start with the fundamentals: {text}"
        elif difficulty == "Advanced":
            text = f"Answer with trade-offs and a practical example: {text}"
        questions.append({"topic": topic, "text": text})
    return questions


def tokenise(text):
    return re.findall(r"[a-zA-Z][a-zA-Z'-]*", text.lower())


def evaluate(question, answer):
    tokens, unique = tokenise(answer), set(tokenise(answer))
    count = len(tokens)
    sentences = max(1, len(re.findall(r"[.!?]", answer)))
    example = bool(re.search(r"\b(example|instance|project|situation|when i|worked)\b", answer, re.I))
    structure = bool(re.search(r"\b(first|second|finally|because|therefore|step|result|task|action)\b", answer, re.I))
    confidence = bool(re.search(r"\b(i would|i can|i have|my approach|i believe|i learned)\b", answer, re.I))
    hits = len(unique & set(tokenise(question["topic"] + " " + question["text"])))
    length = min(2.5, count / 35)
    relevance = min(2.5, 1 + hits * .3 + (.5 if count > 35 else 0))
    clarity = min(2, .8 + (.5 if sentences > 1 else 0) + (.4 if structure else 0))
    completeness = min(2, .5 + (.7 if example else 0) + (.4 if count >= 60 else 0) + (.4 if structure else 0))
    communication = min(1, .35 + (.35 if confidence else 0) + (.3 if sentences > 1 else 0))
    score = round(max(0, min(10, length + relevance + clarity + completeness + communication)), 1)
    if count < 12: score = min(score, 3.5)
    strengths = [text for text, condition in [("You gave enough context to make your thinking understandable.", count >= 35), ("A concrete example makes the answer more credible.", example), ("Your answer shows a useful step-by-step structure.", structure), ("Your language communicates ownership and confidence.", confidence)] if condition]
    if not strengths: strengths = ["You made a direct attempt and created a starting point to build on."]
    missing = [text for text, condition in [("More detail and reasoning", count < 35), ("A specific example or outcome", not example), ("A clear beginning, middle, and conclusion", not structure), (f"Role-specific {question['topic'].lower()} vocabulary", hits == 0)] if condition]
    if not missing: missing = ["A sharper result or measurable impact"]
    behavioral = question["topic"] in {"Introduction", "Strengths", "Weaknesses", "Teamwork", "Conflict", "Leadership", "Career goals", "Projects", "Internships"}
    improved = "Start with the main idea, add one specific example, and close with the result. " + ("Use context, action, and result to keep the story focused." if behavioral else "Name the core concept, explain the trade-off, and connect it to practice.")
    return {"score": score, "relevance": round(min(10, relevance * 4), 1), "technical": round(min(10, hits * 1.5 + length * 2.2 + 2), 1), "clarity": round(min(10, clarity * 4), 1), "completeness": round(min(10, completeness * 4), 1), "communication": round(min(10, communication * 10), 1), "strengths": strengths, "missing": missing, "improved": improved, "feedback": "Solid foundation. Add one specific example and make the outcome explicit." if score >= 6 else "Keep going. Explain your reasoning and support it with a concrete example.", "tip": "Use STAR: Situation, Task, Action, Result." if behavioral else "Mention a trade-off, example, or measurable result to make the answer memorable."}


def build_report(data):
    evaluations = [item["evaluation"] for item in data["answers"]]
    scores = [item["score"] for item in data["answers"]]
    avg = sum(scores) / len(scores) if scores else 0
    categories = {"Technical Knowledge": round(sum(e["technical"] for e in evaluations) / len(evaluations), 1), "Communication": round(sum(e["communication"] for e in evaluations) / len(evaluations), 1), "Clarity": round(sum(e["clarity"] for e in evaluations) / len(evaluations), 1), "Problem Solving": round(sum(e["relevance"] for e in evaluations) / len(evaluations), 1), "Completeness": round(sum(e["completeness"] for e in evaluations) / len(evaluations), 1)}
    weak = [name for name, value in categories.items() if value < 6] or ["Deeper examples and measurable outcomes"]
    topics = (weak[:3] + [data["profile"]["role"] + " practice"]) * 2
    plan = [{"day": i + 1, "title": title, "detail": "Review one concept, write a short explanation, then answer one timed practice question."} for i, title in enumerate(topics[:7])]
    return {"overall": round(avg * 10), "attempted": sum(item["answer"] != "Skipped" for item in data["answers"]), "categories": categories, "strengths": ["Consistent participation across the interview."] + (["Your communication style is becoming more confident."] if categories["Communication"] >= 6 else []), "weaknesses": weak, "feedback": f"You completed a {data['profile']['role']} practice session with an average answer score of {round(avg * 10)}/100. Focused repetition on weaker categories will make your responses more structured and persuasive.", "plan": plan, "created": datetime.now().strftime("%d %b %Y")}


@app.route("/")
def index(): return render_template("index.html")


@app.route("/setup", methods=["GET", "POST"])
def setup():
    form = request.form.to_dict() if request.method == "POST" else {}
    context = {"form": form, "roles": ROLES, "experiences": EXPERIENCE, "types": INTERVIEW_TYPES, "counts": QUESTION_COUNTS}
    if request.method == "POST":
        required = ["name", "role", "experience", "interview_type", "question_count"]
        valid = all(form.get(key, "").strip() for key in required)
        try: valid = valid and form["role"] in ROLES and form["experience"] in EXPERIENCE and form["interview_type"] in INTERVIEW_TYPES and int(form["question_count"]) in QUESTION_COUNTS
        except (KeyError, ValueError): valid = False
        if not valid: return render_template("setup.html", error="Complete every field using the provided options.", **context)
        count = int(form["question_count"])
        profile = {"name": form["name"].strip(), "role": form["role"], "experience": form["experience"], "interview_type": form["interview_type"], "question_count": count}
        session["interview"] = {"profile": profile, "questions": make_questions(profile["role"], count, profile["experience"]), "answers": [], "current_index": 0, "feedback": None, "report": None}
        return redirect(url_for("interview"))
    return render_template("setup.html", **context)


@app.route("/interview")
@guarded
def interview():
    data = session["interview"]
    if data["report"]: return redirect(url_for("report"))
    return render_template("interview.html", data=data, item=data["questions"][data["current_index"]], index=data["current_index"], total=len(data["questions"]))


@app.route("/submit-answer", methods=["POST"])
@guarded
def submit_answer():
    data = session["interview"]
    answer = request.form.get("answer", "").strip()
    if not answer:
        flash("Write an answer before submitting, or skip this question.", "error")
        return redirect(url_for("interview"))
    index = data["current_index"]
    evaluation = evaluate(data["questions"][index], answer)
    data["answers"] = [item for item in data["answers"] if item["index"] != index]
    data["answers"].append({"index": index, "question": data["questions"][index], "answer": answer, "evaluation": evaluation, "score": evaluation["score"]})
    data["feedback"] = evaluation
    session.modified = True
    return redirect(url_for("feedback"))


@app.route("/feedback")
@guarded
def feedback():
    data = session["interview"]
    if not data.get("feedback"): return redirect(url_for("interview"))
    return render_template("feedback.html", data=data, item=data["questions"][data["current_index"]], evaluation=data["feedback"], index=data["current_index"], total=len(data["questions"]))


@app.route("/next-question", methods=["POST"])
@guarded
def next_question():
    data = session["interview"]
    if data["current_index"] + 1 >= len(data["questions"]):
        data["report"] = build_report(data)
        session.modified = True
        return redirect(url_for("report"))
    data["current_index"] += 1
    data["feedback"] = None
    session.modified = True
    return redirect(url_for("interview"))


@app.route("/skip-question", methods=["POST"])
@guarded
def skip_question():
    data = session["interview"]
    index = data["current_index"]
    evaluation = evaluate(data["questions"][index], "")
    evaluation.update({"score": 0, "strengths": ["You kept the session moving."], "missing": ["A submitted answer", "Specific reasoning and examples"], "feedback": "This question was skipped. Use the next one to practice thinking out loud."})
    data["answers"] = [item for item in data["answers"] if item["index"] != index]
    data["answers"].append({"index": index, "question": data["questions"][index], "answer": "Skipped", "evaluation": evaluation, "score": 0})
    data["feedback"] = evaluation
    session.modified = True
    return redirect(url_for("feedback"))


@app.route("/previous-question", methods=["POST"])
@guarded
def previous_question():
    data = session["interview"]
    data["current_index"] = max(0, data["current_index"] - 1)
    data["feedback"] = None
    session.modified = True
    return redirect(url_for("interview"))


@app.route("/report")
@guarded
def report():
    data = session["interview"]
    if not data.get("report"): return redirect(url_for("interview"))
    return render_template("report.html", data=data, report=data["report"], printable=False)


@app.route("/preparation")
@guarded
def preparation():
    data = session["interview"]
    if not data.get("report"): return redirect(url_for("report"))
    return render_template("preparation.html", data=data, report=data["report"])


@app.route("/download-report")
@guarded
def download_report():
    data = session["interview"]
    if not data.get("report"): return redirect(url_for("report"))
    return render_template("report.html", data=data, report=data["report"], printable=True)


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("setup"))


@app.errorhandler(500)
def error_500(_error):
    flash("Something went wrong while loading that view. Please try again.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
