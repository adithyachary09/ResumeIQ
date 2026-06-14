import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from resume_parser import extract_text_from_pdf
from analyzer import analyze_resume

app = FastAPI(title="ResumeIQ API")

# Configure CORS for all origins (makes frontend integration easier)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint to prevent 404 errors on the base URL."""
    return {"message": "Welcome to the ResumeIQ API. Access /health for status or use /analyze to process resumes."}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment status."""
    return {"status": "ok", "message": "ResumeIQ API is running."}

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    target_role: str = Form("")
):
    """
    Main endpoint: 
    1. Validates the PDF and JD.
    2. Extracts text from the PDF.
    3. Sends text to Gemini for analysis.
    4. Returns strict JSON.
    """
    # 1. Validate Job Description length
    if len(jd_text) < 100:
        raise HTTPException(status_code=400, detail="Job description must be at least 100 characters long.")

    # 2. Validate File Type
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # 3. Read File and Validate Size (Max 5MB)
    file_bytes = await resume.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 5MB limit.")

    # 4. Extract Text
    resume_text = extract_text_from_pdf(file_bytes)
    if resume_text.startswith("Error:"):
        raise HTTPException(status_code=400, detail=resume_text)

    # 5. Analyze with Gemini
    ai_response_string = analyze_resume(resume_text, jd_text, target_role)
    
    # 6. Parse and Return JSON
    try:
        # Convert Gemini's JSON string into a Python dictionary 
        # so FastAPI automatically serves it as proper application/json
        result_dict = json.loads(ai_response_string)
        return result_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI response into JSON.")