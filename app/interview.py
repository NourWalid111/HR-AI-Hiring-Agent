def create_interview_invitation(candidate):
    """
    Create a personalized interview invitation draft.

    The message is only drafted.
    It is NOT automatically sent.
    """

    candidate_name = candidate["candidate_name"]
    score = candidate["overall_score"]

    message = f"""
Subject: Interview Invitation — Junior AI Engineer

Dear {candidate_name},

Thank you for your interest in the Junior AI Engineer position.

After reviewing your application, we would like to invite you
to an interview with our AI engineering team.

Your application achieved an internal screening score of
{score:.2f} during our automated screening process.

The interview will give us an opportunity to discuss your
experience, technical background, and the role in more detail.

Our HR team will contact you with the available interview
times and next steps.

Best regards,
HR Team
"""

    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_name": candidate_name,
        "score": score,
        "message": message.strip(),
        "status": "pending_approval"
    }


def create_interview_drafts(shortlisted_candidates):

    drafts = []

    for candidate in shortlisted_candidates:

        draft = create_interview_invitation(
            candidate
        )

        drafts.append(draft)

    return drafts


def print_interview_queue(drafts):

    print("\n==============================")
    print("INTERVIEW APPROVAL QUEUE")
    print("==============================")

    if not drafts:
        print("No interview drafts.")
        return

    for draft in drafts:

        print(
            f"\nCandidate: {draft['candidate_name']}"
        )

        print(
            f"Score: {draft['score']}"
        )

        print(
            f"Status: {draft['status']}"
        )

        print("\nDraft:")
        print(draft["message"])