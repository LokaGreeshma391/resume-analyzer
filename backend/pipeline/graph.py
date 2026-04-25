import os
import requests
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from pipeline.agents import get_llm

load_dotenv()

# ─── State ───────────────────────────────────────────────
class ResumeState(TypedDict):
    resume: str
    job_description: str
    analysis: Optional[str]
    gaps: Optional[str]
    match_score: Optional[int]
    path_decision: Optional[Literal["rewrite", "skip"]]
    enhanced_resume: Optional[str]
    job_suggestions: Optional[str]

# ─── Nodes ───────────────────────────────────────────────
def analyze_node(state: ResumeState) -> ResumeState:
    llm = get_llm()
    prompt = f"""You are an expert resume reviewer.
Analyze the resume below. List its key strengths and weaknesses clearly.

Resume:
{state['resume']}"""
    result = llm.invoke(prompt)
    return {**state, "analysis": result.content}


def match_node(state: ResumeState) -> ResumeState:
    llm = get_llm()
    prompt = f"""You are a senior tech recruiter.
Compare this resume against the job description.
List specific skill gaps, missing keywords, and mismatches.

Resume:
{state['resume']}

Job Description:
{state['job_description']}"""
    result = llm.invoke(prompt)
    return {**state, "gaps": result.content}
def score_node(state: ResumeState) -> ResumeState:
    llm = get_llm()
    prompt = f"""You are a resume scoring expert.
Based on this resume and job description, give a match score from 0 to 100.
Only reply with a single integer number. Nothing else. No explanation.

Resume:
{state['resume']}

Job Description:
{state['job_description']}"""
    result = llm.invoke(prompt).content.strip()
    try:
        score = int(''.join(filter(str.isdigit, result)))
        score = max(0, min(100, score))
    except:
        score = 50
    return {**state, "match_score": score}


def evaluate_node(state: ResumeState) -> ResumeState:
    llm = get_llm()
    prompt = f"""Based on these gaps between the resume and job description:

{state['gaps']}

Does the resume need significant rewriting to match the job?
Reply with ONLY one word: rewrite or skip."""
    result = llm.invoke(prompt).content.lower().strip()
    decision = "rewrite" if "rewrite" in result else "skip"
    return {**state, "path_decision": decision}


def rewrite_node(state: ResumeState) -> ResumeState:
    llm = get_llm()
    prompt = f"""You are a professional resume writer.
Rewrite and enhance the resume below to better match the job description.
Add missing keywords, quantify achievements, and improve language.

Resume:
{state['resume']}

Job Description:
{state['job_description']}

Gaps to fix:
{state['gaps']}"""
    result = llm.invoke(prompt)
    return {**state, "enhanced_resume": result.content}


def jobs_node(state: ResumeState) -> ResumeState:
    api_key = os.getenv("SERPER_API_KEY")
    query = state['job_description'][:120].split('\n')[0]

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            },
            json={"q": f"{query} jobs 2025", "num": 5},
            timeout=10
        )
        data = response.json()
        results = data.get("organic", [])[:5]
        jobs_text = "\n\n".join([
            f"**{r.get('title', 'Job')}**\n{r.get('snippet', '')}\n{r.get('link', '')}"
            for r in results
        ])
    except Exception as e:
        jobs_text = f"Could not fetch jobs: {str(e)}"

    return {**state, "job_suggestions": jobs_text}


# ─── Graph ───────────────────────────────────────────────
def build_graph():
    builder = StateGraph(ResumeState)

    builder.add_node("Analyze", analyze_node)
    builder.add_node("Match", match_node)
    builder.add_node("Score", score_node)
    builder.add_node("Evaluate", evaluate_node)
    builder.add_node("Rewrite", rewrite_node)
    builder.add_node("Jobs", jobs_node)

    builder.set_entry_point("Analyze")
    builder.add_edge("Analyze", "Match")
    builder.add_edge("Match", "Score")
    builder.add_edge("Score", "Evaluate")
    builder.add_conditional_edges(
        "Evaluate",
        lambda s: s["path_decision"],
        {"rewrite": "Rewrite", "skip": "Jobs"}
    )
    builder.add_edge("Rewrite", "Jobs")
    builder.add_edge("Jobs", END)

    return builder.compile()

graph = build_graph()