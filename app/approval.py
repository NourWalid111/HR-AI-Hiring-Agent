def request_human_approval(draft):
    """
    Request a human HR decision.

    The system does NOT automatically send the invitation.
    """

    print("\n==============================")
    print("HUMAN APPROVAL REQUIRED")
    print("==============================")

    print(
        f"\nCandidate: {draft['candidate_name']}"
    )

    print(
        f"Screening Score: {draft['score']}"
    )

    print("\nInterview Draft:")
    print("------------------------------")
    print(draft["message"])
    print("------------------------------")

    while True:

        decision = input(
            "\nHR Decision [approve/reject]: "
        ).strip().lower()

        if decision == "approve":
            print("\nInterview invitation APPROVED.")
            return "approved"

        if decision == "reject":
            print("\nInterview invitation REJECTED.")
            return "rejected"

        print(
            "Invalid decision. "
            "Please enter 'approve' or 'reject'."
        )