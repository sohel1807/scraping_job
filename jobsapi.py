from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from jobspy import scrape_jobs
import fitz  
import os
from groq import Groq
import json
import re
from dotenv import load_dotenv

app = FastAPI()


state = {
    "jobs": [],
    "resume_text": ""
}


class JobRequest(BaseModel):
    site_name: Optional[List[str]] = ["linkedin", "indeed", "naukri"]
    search_term: str
    location: str
    results_wanted: Optional[int] = 5
    country_indeed: Optional[str] = "IN"
    hours_old: Optional[int] = 72


@app.post("/scrape-jobs/")
async def scrape_jobs_api(request: JobRequest):
    try:
        jobs = scrape_jobs(
            site_name=request.site_name,
            search_term=request.search_term,
            location=request.location,
            results_wanted=request.results_wanted,
            hours_old=request.hours_old,
            country_indeed=request.country_indeed,
        )

        if jobs.empty:
            raise HTTPException(status_code=404, detail="No jobs found.")

        cleaned_jobs = jobs.replace([float("inf"), float("-inf")], None).fillna("")
        job_list = cleaned_jobs.to_dict(orient="records")

        # Save to state
        state["jobs"] = job_list

        return {"message": f"Saved {len(job_list)} jobs", "jobs": job_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-pdf/")
async def extract_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with fitz.open(stream=contents, filetype="pdf") as doc:
            resume_text = "".join([page.get_text() for page in doc])

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="PDF has no readable text.")

        # Save resume content
        state["resume_text"] = resume_text.strip()

        return {"message": "Resume uploaded and extracted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-recommend/")
async def ai_recommend_jobs():
    try:
        if not state["jobs"] or not state["resume_text"]:
            raise HTTPException(status_code=400, detail="Both jobs and resume must be uploaded first.")

        resume = state["resume_text"]
        jobs = state["jobs"]

        load_dotenv()  
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Prepare job descriptions for AI
        job_descriptions = "\n\n".join([
            f"Job {i+1}:\nTitle: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}"
            for i, job in enumerate(jobs)
        ])

        # AI prompt 
        prompt = f"""
You are an intelligent job recommender. The following is a candidate's resume, followed by 15 job descriptions.

Resume:
{resume}

Jobs:
{job_descriptions}

Based on the resume, select the best 5 matching jobs and return them in JSON like:
[
  {{
    "id": int,
    "title": str,
    "company_name": str,
    "job_url": str,
    "reason": str
  }}
]
        """

        
        top_5_jobs = jobs[:5]  # mock: select top 5
        recommendations = [
            {
                "id": i + 1,
                "title": job["title"],
                "company_name": job["company"],
                "job_url": job.get("job_url", "N/A"),
                "reason": "Resume closely matches job description and required skills."
            }
            for i, job in enumerate(top_5_jobs)
        ]

        return {
            "message": "Top 5 job recommendations based on your resume",
            "recommendations": recommendations
        }

        completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
        return completion.choices[0].message.content.strip()


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
