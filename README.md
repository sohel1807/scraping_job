Sure! Here's a **short and focused `README.md`** that includes only:

* Project purpose
* Basic flow
* Required `.env`
* `POST` endpoints

---

### ✅ Minimal `README.md`

```markdown
# 🧠 AI Job Recommendation API (FastAPI + Groq)

This FastAPI service scrapes job listings, extracts resume text from a PDF, and uses Groq's Mixtral model to recommend the top 5 job matches based on your resume.

---

## 🔁 Flow

1. **POST /scrape-jobs/** – Scrapes 15 jobs from LinkedIn, Indeed, Naukri.
2. **POST /extract-pdf/** – Upload your resume (PDF) and extract text.
3. **POST /ai-recommend/** – AI matches your resume with job descriptions and returns the top 5.

---

## 🔐 .env Required

Create a `.env` file with your Groq API key:

```

GROQ\_API\_KEY=your\_groq\_api\_key\_here

````

---

## 🔗 POST Endpoints Summary

### `/scrape-jobs/`

```json
{
  "search_term": "Data Analyst",
  "location": "Bangalore"
}
````

### `/extract-pdf/`

* Form field: `file` (upload PDF)

### `/ai-recommend/`

* No input body (uses stored jobs + resume text)



