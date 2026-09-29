from pydantic import BaseModel, Field


class SkillEvaluation(BaseModel):
    skill: str
    category: str
    score: float = Field(ge=0, le=100)
    years_experience: float = Field(ge=0)
    evidence: str


class CandidateEvaluation(BaseModel):
    candidate_name: str
    relevant_experience_years: float = Field(ge=0)
    skills: list[SkillEvaluation]
    strengths: list[str]
    gaps: list[str]
    evidence: list[str]


class CriticResult(BaseModel):
    passed: bool
    issues: list[str]
    unsupported_skills: list[str]
    explanation: str


class RetryResult(BaseModel):
    success: bool
    attempts: int
    error: str | None = None
    