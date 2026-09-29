from app.models import SkillEvaluation, CandidateEvaluation
from app.scoring import calculate_overall_score


def main():

    evaluation = CandidateEvaluation(
        candidate_name="Test Candidate",
        relevant_experience_years=2.0,

        skills=[
            SkillEvaluation(
                skill="Python",
                category="required",
                score=80,
                years_experience=2.0,
                evidence="Two years of Python development."
            ),
            SkillEvaluation(
                skill="SQL",
                category="required",
                score=70,
                years_experience=1.5,
                evidence="Used SQL with relational databases."
            ),
            SkillEvaluation(
                skill="Docker",
                category="preferred",
                score=60,
                years_experience=1.0,
                evidence="Used Docker for application deployment."
            ),
        ],

        strengths=[
            "Python",
            "SQL"
        ],

        gaps=[
            "Limited preferred-skill experience"
        ],

        evidence=[
            "Two years of Python development.",
            "Used SQL with relational databases.",
            "Used Docker for application deployment."
        ]
    )

    scores = calculate_overall_score(evaluation)

    print("\n==============================")
    print("SCORING TEST")
    print("==============================")

    print(f"Candidate: {evaluation.candidate_name}")
    print(f"Required Score: {scores['required_score']}")
    print(f"Experience Score: {scores['experience_score']}")
    print(f"Preferred Score: {scores['preferred_score']}")
    print(f"Background Score: {scores['background_score']}")
    print(f"Overall Score: {scores['overall_score']}")

    assert scores["required_score"] == 75.0
    assert scores["experience_score"] == 100.0
    assert scores["preferred_score"] == 60.0
    assert scores["overall_score"] == 71.5

    print("\nSCORING TEST PASSED")


if __name__ == "__main__":
    main()