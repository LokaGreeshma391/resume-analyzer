from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pipeline.graph import graph
from utils.pdf_parser import extract_text_from_pdf
from database import save_run, get_all_runs, get_run_by_id

load_dotenv()

app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Resume Analyzer API is running"}

@app.post("/analyze")
async def analyze(
    resume_pdf: UploadFile = File(...),
    job_description: str = Form(...)
):
    pdf_bytes = await resume_pdf.read()
    resume_text = extract_text_from_pdf(pdf_bytes)

    result = graph.invoke({
        "resume": resume_text,
        "job_description": job_description,
        "analysis": None,
        "gaps": None,
        "path_decision": None,
        "enhanced_resume": None,
        "job_suggestions": None,
    })

    run_id = save_run({
        "analysis":         result["analysis"],
        "gaps":             result["gaps"],
        "enhanced_resume":  result.get("enhanced_resume", ""),
        "job_suggestions":  result.get("job_suggestions", ""),
    })

    return {
        "run_id":          run_id,
        "analysis":        result["analysis"],
        "gaps":            result["gaps"],
        "match_score":     result.get("match_score", 0),
        "enhanced_resume": result.get("enhanced_resume"),
        "job_suggestions": result.get("job_suggestions"),
    }

@app.get("/history")
def history():
    runs = get_all_runs()
    return [
        {
            "id":         r.id,
            "created_at": str(r.created_at),
            "preview":    (r.analysis or "")[:200] + "..."
        }
        for r in runs
    ]

@app.get("/history/{run_id}")
def history_detail(run_id: int):
    run = get_run_by_id(run_id)
    if not run:
        return {"error": "Not found"}
    return {
        "id":               run.id,
        "created_at":       str(run.created_at),
        "analysis":         run.analysis,
        "gaps":             run.gaps,
        "enhanced_resume":  run.enhanced_resume,
        "job_suggestions":  run.job_suggestions,
    }