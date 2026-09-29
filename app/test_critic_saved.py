from app.agents import critique_candidate
from app.tools import ingest_resumes


def main():

    resumes = ingest_resumes()

    resume = resumes[0]

    # This is the evaluation produced by the previous
    # successful Gemini call.
    #
    # We load it manually so we DON'T call the evaluator again.

    from app.models import (
        CandidateEvaluation,
        SkillEvaluation
    )

    evaluation = CandidateEvaluation(
        candidate_name="Karim Hassan",
        relevant_experience_years=1.92,
        skills=[
            SkillEvaluation(
                skill="Python",
                category="required",
                score=75,
                years_experience=1.0,
                evidence="Listed under Technical Skills; used in internship for FastAPI API work and in Task Management API project."
            ),
            SkillEvaluation(
                skill="Machine Learning",
                category="required",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="Deep Learning",
                category="required",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="SQL",
                category="required",
                score=85,
                years_experience=1.67,
                evidence="Listed under Technical Skills; designed PostgreSQL schemas and optimized SQL queries at NileTech Solutions."
            ),
            SkillEvaluation(
                skill="REST APIs",
                category="required",
                score=90,
                years_experience=1.92,
                evidence="Developed REST APIs using Node.js/Express at NileTech Solutions and FastAPI during internship."
            ),
            SkillEvaluation(
                skill="Git",
                category="required",
                score=80,
                years_experience=1.92,
                evidence="Listed under Tools in Technical Skills."
            ),
            SkillEvaluation(
                skill="PyTorch or TensorFlow",
                category="preferred",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="Hugging Face",
                category="preferred",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="RAG",
                category="preferred",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="Vector databases",
                category="preferred",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="LangChain",
                category="preferred",
                score=0,
                years_experience=0,
                evidence="No evidence provided in the resume."
            ),
            SkillEvaluation(
                skill="Docker",
                category="preferred",
                score=70,
                years_experience=1.0,
                evidence="Listed under Tools in Technical Skills."
            ),
            SkillEvaluation(
                skill="Cloud computing",
                category="preferred",
                score=65,
                years_experience=0.5,
                evidence="AWS fundamentals listed under Technical Skills; AWS Cloud Practitioner certified (2025)."
            )
        ],
        strengths=[
            "Strong backend and full-stack software development experience with Python, REST APIs, SQL, and Docker.",
            "Meets general software engineering experience requirements (~1.92 years across junior role and internship).",
            "Certified AWS Cloud Practitioner with foundational cloud computing knowledge."
        ],
        gaps=[
            "Lacks experience or evidence in Machine Learning and Deep Learning required skills.",
            "No demonstrated experience with preferred AI/ML technologies such as PyTorch, TensorFlow, Hugging Face, RAG, Vector databases, or LangChain."
        ],
        evidence=[
            "Resume highlights backend web development (Node.js, FastAPI, PostgreSQL, REST APIs) but contains no references to AI/ML framework usage, modeling, or RAG architectures."
        ]
    )

    print("\n==============================")
    print("RUNNING EVIDENCE CRITIC")
    print("==============================")

    critique = critique_candidate(
        resume_text=resume["text"],
        evaluation=evaluation
    )

    print("\n==============================")
    print("CRITIC RESULT")
    print("==============================")

    print(
        critique.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()