REQUIRED_WEIGHT = 0.50
EXPERIENCE_WEIGHT = 0.25
PREFERRED_WEIGHT = 0.15
BACKGROUND_WEIGHT = 0.10


def calculate_skill_score(
    skills: list,
    category: str
) -> float:

    category_skills = [
        skill
        for skill in skills
        if skill.category.lower() == category.lower()
    ]

    if not category_skills:
        return 0.0

    total = sum(
        skill.score
        for skill in category_skills
    )

    return total / len(category_skills)


def calculate_experience_score(
    years: float,
    required_years: float = 1.0
) -> float:

    if years <= 0:
        return 0.0

    score = (
        years / required_years
    ) * 100

    return min(score, 100.0)


def calculate_overall_score(
    evaluation
) -> dict:

    required_score = calculate_skill_score(
        evaluation.skills,
        "required"
    )

    preferred_score = calculate_skill_score(
        evaluation.skills,
        "preferred"
    )

    experience_score = calculate_experience_score(
        evaluation.relevant_experience_years
    )

    background_score = 0.0

    overall_score = (
        required_score * REQUIRED_WEIGHT
        + experience_score * EXPERIENCE_WEIGHT
        + preferred_score * PREFERRED_WEIGHT
        + background_score * BACKGROUND_WEIGHT
    )

    return {
        "required_score": round(
            required_score,
            2
        ),
        "experience_score": round(
            experience_score,
            2
        ),
        "preferred_score": round(
            preferred_score,
            2
        ),
        "background_score": round(
            background_score,
            2
        ),
        "overall_score": round(
            overall_score,
            2
        )
    }