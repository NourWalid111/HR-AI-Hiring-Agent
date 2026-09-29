import os
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models import (
    CandidateEvaluation,
    CriticResult
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GEMINI MODEL
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================================
# STRUCTURED OUTPUT MODELS
# ============================================================

structured_llm = llm.with_structured_output(
    CandidateEvaluation
)

critic_llm = llm.with_structured_output(
    CriticResult
)


# ============================================================
# SAFE GEMINI INVOCATION
# ============================================================

def safe_invoke(
    llm_chain,
    prompt,
    max_retries=1
):
    """
    Safely invoke a Gemini chain.

    Rate-limit/quota errors are reported immediately.
    Other temporary errors may be retried.
    """

    for attempt in range(max_retries + 1):

        try:
            return llm_chain.invoke(prompt)

        except Exception as e:

            error_message = str(e)

            # ------------------------------------------------
            # GEMINI QUOTA / RATE LIMIT
            # ------------------------------------------------

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            ):

                raise RuntimeError(
                    "Gemini API quota exceeded. "
                    "Please wait for the quota to reset "
                    "or use a Gemini API project with "
                    "available quota."
                ) from e

            # ------------------------------------------------
            # TEMPORARY API / NETWORK ERROR
            # ------------------------------------------------

            temporary_errors = [
    "timeout",
    "connection",
    "temporarily unavailable",
    "internal server error",
    "503",
    "unavailable",
    "high demand"
]

            if any(
                keyword in error_message.lower()
                for keyword in temporary_errors
            ):

                if attempt < max_retries:

                    wait_time = 5 * (attempt + 1)

                    print(
                        f"Temporary Gemini error. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

                raise RuntimeError(
                    "Gemini API failed after retries."
                ) from e

            # ------------------------------------------------
            # UNKNOWN ERROR
            # ------------------------------------------------

            raise
def evaluate_candidate(
    resume_text: str,
    job_description: str,
    critic_feedback: str = ""
) -> CandidateEvaluation:

    retry_instructions = ""

    if critic_feedback:

        retry_instructions = f"""
PREVIOUS EVALUATION FEEDBACK:

A previous evaluation was rejected by the validation agent.

The validation agent reported:

{critic_feedback}

You MUST carefully review the original resume again and
correct the problems identified above.

Do not blindly repeat the previous evaluation.

Make sure every score and every claim is supported by
the resume.
"""

    prompt = f"""
You are an HR screening AI agent.

Your task is to analyze a candidate's resume against
the provided job description.

IMPORTANT RULES:

1. Use ONLY information supported by the resume.
2. Never invent skills or experience.
3. Every skill score must have evidence.
4. If there is no evidence for a skill, give it a score of 0
   and explicitly state that there is no evidence.
5. Do not assume that absence of a skill means the candidate
   definitely lacks it.
6. Be conservative when estimating years of experience.
7. Classify each evaluated skill as either:
   - required
   - preferred
8. Do NOT calculate a final overall candidate score.
9. Do NOT make the final hiring decision.
10. Provide concise evidence that an HR reviewer can inspect.

{retry_instructions}

JOB DESCRIPTION:

{job_description}

CANDIDATE RESUME:

{resume_text}

Extract and evaluate the candidate's relevant skills,
experience, strengths, gaps, and supporting evidence.
"""

    result = safe_invoke(
        structured_llm,
        prompt
    )

    return result

def critique_candidate(
    resume_text: str,
    evaluation: CandidateEvaluation
) -> CriticResult:

    prompt = f"""
You are a strict validation and reflection agent reviewing
an HR candidate evaluation.

Your job is NOT to re-score the candidate.

Your job is to independently verify whether the evaluator's
claims and scores are supported by the ORIGINAL RESUME.

You have two sources of information:

1. ORIGINAL RESUME
2. CANDIDATE EVALUATION produced by another AI agent

You must compare them carefully.

CHECK THE FOLLOWING:

1. Does every evaluated skill have evidence in the original resume?
2. Is the evidence actually relevant to that skill?
3. Is the assigned score reasonably consistent with the evidence?
4. Are the stated years of experience supported by the resume?
5. Did the evaluator invent any skill, project, job, certification,
   or experience?
6. Are there unsupported claims in strengths or evidence?
7. Are skills scored 0 correctly when the resume provides no evidence?
8. Did the evaluator incorrectly claim that a candidate has a skill
   when the resume does not support it?

IMPORTANT RULES:

- The ORIGINAL RESUME is the source of truth.
- Do not trust the evaluator automatically.
- Do not invent information.
- Do not assume missing information.
- A skill mentioned only indirectly should not automatically receive
  a high score.
- A score of 0 with no evidence is acceptable.
- If the evaluator's evidence cannot be found in the resume,
  identify it as an issue.
- If a score is clearly inconsistent with the resume evidence,
  identify it as an issue.
- If years of experience are unsupported or exaggerated,
  identify it as an issue.
- Be strict but fair.

ORIGINAL RESUME:

{resume_text}

CANDIDATE EVALUATION:

{evaluation.model_dump_json(indent=2)}

Return a structured critique.

The field "passed" should be TRUE only if the evaluation is
adequately supported by the original resume.

If the evaluation contains unsupported claims, set "passed"
to FALSE and list the problems in "issues".

For "unsupported_skills", list the specific skills whose
scores or claims are not supported by the original resume.

Explain your reasoning briefly in "explanation".
"""

    result = safe_invoke(
        critic_llm,
        prompt
    )

    return result