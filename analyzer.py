import os
import json
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class ScoreBreakdown(BaseModel):
    keyword_match: int
    formatting: int
    experience_relevance: int
    skills_alignment: int
    education_match: int

class SectionFeedback(BaseModel):
    summary: str
    experience: str
    skills: str
    education: str
    projects: str

class ResumeAnalysis(BaseModel):
    ats_score: int
    score_breakdown: ScoreBreakdown
    matched_keywords: list[str]
    missing_keywords: list[str]
    section_feedback: SectionFeedback
    top_improvements: list[str]
    rewritten_summary: str
    interview_probability: str
    candidate_strengths: list[str]
    red_flags: list[str]

def analyze_resume(resume_text: str, jd_text: str, target_role: str = "") -> str:
    """
    Sends the extracted resume text and job description to Gemini 3.1 Flash Lite 
    and forces a strict JSON response matching the Pydantic schema.
    """
    try:
        client = genai.Client()
        
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) and technical recruiter.
        Analyze the following resume against the provided job description.
        
        Target Role: {target_role if target_role else 'Not specified'}
        
        Job Description:
        {jd_text}
        
        Resume:
        {resume_text}
        """
        
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeAnalysis,
                temperature=0.2, 
            ),
        )
        
        return response.text
        
    except Exception as e:
        error_response = {
            "ats_score": 0,
            "error": f"Failed to analyze resume. Details: {str(e)}"
        }
        return json.dumps(error_response)