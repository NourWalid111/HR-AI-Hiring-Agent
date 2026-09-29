from app.graph import build_hr_graph

from app.tools import (
    ingest_resumes,
    detect_duplicate_files
)

from app.database import initialize_database


def main():

    initialize_database()

    print("\n==============================")
    print("STARTING FINAL HR AGENT TEST")
    print("==============================")

    resumes = ingest_resumes()
    resumes = detect_duplicate_files(resumes)

    # Process ONLY ONE non-duplicate resume
    resume = None

    for item in resumes:

        if not item["is_duplicate"]:
            resume = item
            break

    if resume is None:

        print("No valid resume found.")
        return

    print(
        f"\nSelected resume: "
        f"{resume['filename']}"
    )

    with open(
        "job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    hr_graph = build_hr_graph()

    initial_state = {

        "resume": resume,

        "job_description": job_description,

        "retry_count": 0,

        # IMPORTANT:
        # Maximum ONE evaluation retry
        "max_retries": 1,

        "retry_feedback": "",

        "status": "started"
    }

    final_state = hr_graph.invoke(
        initial_state
    )

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================")

    print(
        "Status:",
        final_state.get("status")
    )

    if final_state.get("candidate_id"):

        print(
            "Database ID:",
            final_state["candidate_id"]
        )

    if final_state.get("scores"):

        print(
            "Overall Score:",
            final_state["scores"]["overall_score"]
        )

    if final_state.get("ranking"):

        print("\nRanking:")

        for candidate in final_state["ranking"]:

            print(
                f"{candidate['rank']}. "
                f"{candidate['candidate_name']} "
                f"— "
                f"{candidate['overall_score']}"
            )

    if final_state.get("approval_results"):

        print("\nApproval Results:")

        for result in final_state[
            "approval_results"
        ]:

            print(
                f"{result['candidate_name']}: "
                f"{result['decision']}"
            )

    if final_state.get("error"):

        print(
            "Error:",
            final_state["error"]
        )


if __name__ == "__main__":
    main()