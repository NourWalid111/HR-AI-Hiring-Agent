from app.database import get_all_candidates


def rank_candidates():
    """
    Retrieve successfully evaluated candidates
    and order them from highest to lowest score.
    """

    candidates = get_all_candidates()

    ranked_candidates = []

    for candidate in candidates:

        if candidate["status"] != "evaluated":
            continue

        ranked_candidates.append({
            "rank": len(ranked_candidates) + 1,
            "candidate_id": candidate["id"],
            "candidate_name": candidate["candidate_name"],
            "filename": candidate["filename"],
            "overall_score": candidate["overall_score"],
            "required_score": candidate["required_score"],
            "experience_score": candidate["experience_score"],
            "preferred_score": candidate["preferred_score"],
            "status": candidate["status"]
        })

    return ranked_candidates


def get_top_candidates(percentage: float = 0.05):

    ranked_candidates = rank_candidates()

    if not ranked_candidates:
        return []

    number_to_select = max(
        1,
        int(len(ranked_candidates) * percentage)
    )

    return ranked_candidates[:number_to_select]


def print_ranking(ranked_candidates):

    print("\n==============================")
    print("CANDIDATE RANKING")
    print("==============================")

    if not ranked_candidates:
        print("No candidates available.")
        return

    for candidate in ranked_candidates:

        print(
            f"{candidate['rank']}. "
            f"{candidate['candidate_name']} "
            f"— "
            f"{candidate['overall_score']}"
        )


def print_shortlist(shortlisted_candidates):

    print("\n==============================")
    print("TOP 5% SHORTLIST")
    print("==============================")

    if not shortlisted_candidates:
        print("No candidates shortlisted.")
        return

    for candidate in shortlisted_candidates:

        print(
            f"Rank {candidate['rank']}: "
            f"{candidate['candidate_name']} "
            f"— Score: {candidate['overall_score']}"
        )