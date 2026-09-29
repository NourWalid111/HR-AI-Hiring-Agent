# HR AI Hiring Agent

An AI-powered HR screening agent that automates the first phase of the hiring process while keeping HR involved in the final decision.

The system ingests resumes, detects duplicates, evaluates candidates against a job description, validates the evaluation with a critic agent, calculates a weighted screening score, ranks candidates, creates interview invitation drafts for the shortlist, and requires human approval before an invitation is approved.

## Project Architecture

```text
Resume Files
     │
     ▼
Resume Ingestion
     │
     ▼
Duplicate Detection
     │
     ▼
┌─────────────────────────────┐
│       LangGraph Agent       │
│                             │
│  Resume → Evaluation        │
│             ↓               │
│          Critic             │
│             ↓               │
│      Retry if necessary     │
│             ↓               │
│          Scoring            │
│             ↓               │
│       SQLite Storage        │
└─────────────────────────────┘
     │
     ▼
Candidate Ranking
     │
     ▼
Top 5% Shortlist
     │
     ▼
Interview Draft
     │
     ▼
Human HR Approval
```

## Main Features

### 1. Resume Ingestion

The system scans the `resumes/` directory and extracts text from supported resume formats.

Supported formats include:

* PDF
* DOCX
* TXT

### 2. Duplicate Detection

Each resume is hashed using SHA-256.

If two files have the same content, the system identifies the later file as a duplicate instead of processing it as a separate candidate.

### 3. Contextual Resume Evaluation

Gemini analyzes the resume against the provided job description.

The evaluation considers:

* Required skills
* Preferred skills
* Relevant experience
* Strengths
* Gaps
* Evidence from the resume

The model is instructed to avoid inventing information and to provide evidence for evaluated skills.

### 4. Structured AI Output

Candidate evaluations are returned using Pydantic models.

Example structure:

```json
{
  "candidate_name": "Candidate Name",
  "relevant_experience_years": 2.0,
  "skills": [
    {
      "skill": "Python",
      "category": "required",
      "score": 85,
      "years_experience": 2,
      "evidence": "Evidence extracted from the resume."
    }
  ],
  "strengths": [
    "Strong Python experience"
  ],
  "gaps": [
    "Limited cloud experience"
  ],
  "evidence": [
    "Evidence supporting the evaluation"
  ]
}
```

### 5. Critic / Reflection Agent

A second AI agent independently checks the evaluation against the original resume.

It verifies:

* Whether evidence exists
* Whether evidence supports the claimed skill
* Whether scores are reasonable
* Whether experience estimates are supported
* Whether unsupported skills were introduced
* Whether strengths and claims are evidence-based

If the critic rejects an evaluation, the workflow can retry the evaluation using the critic's feedback.

### 6. Weighted Candidate Scoring

Candidates receive a standardized screening score based on:

| Component           | Weight |
| ------------------- | -----: |
| Required skills     |    50% |
| Relevant experience |    25% |
| Preferred skills    |    15% |
| Background          |    10% |

The scoring system is deterministic Python code rather than an LLM-generated final score.

### 7. Persistent Storage

Candidate information is stored in SQLite.

The database stores:

* Candidate identity
* Resume filename
* Resume hash
* Relevant experience
* Required skill score
* Experience score
* Preferred skill score
* Background score
* Overall score
* Candidate status
* Individual skill evaluations
* Evidence

### 8. Ranking and Shortlisting

Candidates are sorted by overall screening score.

The system selects the top 5% for the interview stage.

### 9. Human-in-the-Loop Approval

The system generates personalized interview invitation drafts for shortlisted candidates.

The invitation is **not automatically sent**.

An HR user must explicitly approve or reject the draft.

```text
AI Shortlist
     ↓
Interview Draft
     ↓
HR Review
   ↙     ↘
Approve  Reject
```

This keeps the final hiring workflow under human control.

## Technology Stack

* Python
* Gemini API
* LangChain
* LangGraph
* Pydantic
* SQLite
* PyPDF
* python-docx
* python-dotenv

## Project Structure

```text
HR_Agent/
│
├── app/
│   ├── __init__.py
│   ├── tools.py
│   ├── models.py
│   ├── agents.py
│   ├── scoring.py
│   ├── database.py
│   ├── graph.py
│   ├── ranking.py
│   ├── interview.py
│   ├── approval.py
│   └── final_demo.py
│
├── resumes/
│   ├── Karim_Hassan_Fictional_CV.pdf
│   ├── Omar_Adel_Fictional_CV.pdf
│   └── Youssef_Mahmoud_Fictional_CV.docx
│
├── results/
│
├── job_description.txt
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit the real `.env` file to GitHub.

The repository includes `.env.example` as a template.

## Running the Project

The complete workflow is executed with:

```powershell
python -m app.final_demo
```

The final demo:

1. Initializes the database
2. Archives previous candidate results
3. Loads the job description
4. Ingests resumes
5. Detects duplicates
6. Runs the LangGraph candidate workflow
7. Evaluates candidates with Gemini
8. Validates evaluations with the critic agent
9. Calculates screening scores
10. Stores candidates in SQLite
11. Ranks candidates
12. Selects the top 5%
13. Creates interview invitation drafts
14. Requests human approval
15. Saves final results

## Local Testing

The individual components can be tested without making Gemini API calls:

```powershell
python -m app.test_scoring
python -m app.test_database
python -m app.test_ranking
python -m app.test_interview
python -m app.test_approval
```

For syntax checking:

```powershell
python -m py_compile app\agents.py app\database.py app\scoring.py app\tools.py app\graph.py app\ranking.py app\interview.py app\approval.py app\final_demo.py
```

## Output

The final workflow saves machine-readable results in:

```text
results/
├── candidate_evaluations.json
├── ranking.json
├── interview_drafts.json
└── final_run.json
```

These files make the workflow easier to inspect, demonstrate, and reproduce.

## Failure Handling

The system includes handling for:

* Missing or unreadable resumes
* Duplicate resumes
* Gemini quota errors
* Temporary Gemini failures
* Invalid candidate evaluations
* Critic rejection
* Evaluation retry
* Database failures
* Human rejection of interview invitations

A failed candidate does not prevent the remaining candidates from being processed.

## Human Oversight

This project is designed as a screening assistant rather than an autonomous hiring decision-maker.

The AI produces evidence-based evaluations and rankings for HR review. Interview invitations remain pending until a human explicitly approves them.

## Assignment Coverage

The implementation addresses the major requirements of the HR first-phase hiring workflow:

* Resume ingestion
* Contextual resume parsing
* Skill screening and scoring
* Candidate ranking
* Top-candidate shortlisting
* Interview invitation drafting
* Human approval
* Duplicate detection
* AI evaluation reflection/critique
* Structured Pydantic output
* Persistent storage
* Failure handling
* Evidence-based scoring
* Explainable candidate evaluation

## Disclaimer

The resumes included in this project are fictional demonstration data.

The system is intended as an educational AI-agent project demonstrating an HR screening workflow and should not be treated as a complete production hiring system.
