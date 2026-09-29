from app.approval import request_human_approval


def main():

    draft = {
        "candidate_id": 1,
        "candidate_name": "Test Candidate",
        "score": 85.5,
        "message": """
Subject: Interview Invitation — Junior AI Engineer

Dear Test Candidate,

We would like to invite you to an interview
for the Junior AI Engineer position.

Best regards,
HR Team
""".strip(),
        "status": "pending_approval"
    }

    decision = request_human_approval(draft)

    print("\n==============================")
    print("FINAL APPROVAL RESULT")
    print("==============================")

    print(f"Candidate: {draft['candidate_name']}")
    print(f"Decision: {decision.upper()}")

    if decision == "approved":
        print("\nFinal decision: APPROVED")

    elif decision == "rejected":
        print("\nFinal decision: REJECTED")

    else:
        raise ValueError(
            f"Unexpected approval decision: {decision}"
        )

    assert decision in {"approved", "rejected"}

    print("\nAPPROVAL TEST PASSED")


if __name__ == "__main__":
    main()