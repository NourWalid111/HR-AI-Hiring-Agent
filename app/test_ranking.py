from app.ranking import (
    rank_candidates,
    get_top_candidates,
    print_ranking,
    print_shortlist
)


def main():

    print("\n==============================")
    print("RANKING TEST")
    print("==============================")

    ranked_candidates = rank_candidates()

    print_ranking(ranked_candidates)

    shortlisted_candidates = get_top_candidates(percentage=0.05)

    print_shortlist(shortlisted_candidates)

    print("\nRANKING TEST PASSED")


if __name__ == "__main__":
    main()