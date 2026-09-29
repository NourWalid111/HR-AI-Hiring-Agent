from app.interview import (
    create_interview_drafts,
    print_interview_queue
)


def main():

    candidates = [
        {
            "candidate_id": 1,
            "candidate_name": "Test Candidate",
            "overall_score": 85.5
        }
    ]

    drafts = create_interview_drafts(candidates)

    print_interview_queue(drafts)

    assert len(drafts) == 1
    assert drafts[0]["candidate_name"] == "Test Candidate"
    assert drafts[0]["score"] == 85.5
    assert drafts[0]["status"] == "pending_approval"
    assert "Interview Invitation" in drafts[0]["message"]

    print("\nINTERVIEW TEST PASSED")


if __name__ == "__main__":
    main()