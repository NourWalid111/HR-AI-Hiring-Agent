import json
import os
from pathlib import Path

from app.tools import (
    ingest_resumes,
    detect_duplicate_files
)

from app.database import (
    initialize_database,
    archive_existing_candidates,
    update_candidate_status
)

from app.graph import build_candidate_graph

from app.ranking import (
    rank_candidates,
    get_top_candidates,
    print_ranking,
    print_shortlist
)

from app.interview import (
    create_interview_drafts,
    print_interview_queue
)

from app.approval import request_human_approval


JOB_DESCRIPTION_FILE = "job_description.txt"
RESULTS_DIR = Path("results")

# The final demo should normally process all resumes.
MAX_CANDIDATES = None

# Keep the agent retry controlled.
MAX_AGENT_RETRIES = 1


def load_job_description():

    with open(
        JOB_DESCRIPTION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def save_json(filename, data):

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = RESULTS_DIR / filename

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_path


def serialize_evaluation(evaluation):

    if evaluation is None:
        return None

    if hasattr(evaluation, "model_dump"):
        return evaluation.model_dump()

    return evaluation


def serialize_critic(critic_result):

    if critic_result is None:
        return None

    if hasattr(critic_result, "model_dump"):
        return critic_result.model_dump()

    return critic_result


def process_candidate(
    graph,
    resume,
    job_description
):

    state = {
        "resume": resume,
        "job_description": job_description,
        "retry_count": 0,
        "max_retries": MAX_AGENT_RETRIES
    }

    result = graph.invoke(state)

    return result


def main():

    print("\n========================================")
    print("HR AI HIRING AGENT")
    print("FINAL END-TO-END DEMO")
    print("========================================")

    # --------------------------------------------------
    # 1. Initialize database
    # --------------------------------------------------

    print("\n[1/7] Initializing database...")

    initialize_database()

    # Archive results from previous demo runs.
    # This prevents stale evaluations from appearing
    # in the new ranking.
    archive_existing_candidates()

    # --------------------------------------------------
    # 2. Load job description
    # --------------------------------------------------

    print("\n[2/7] Loading job description...")

    job_description = load_job_description()

    print(
        f"Job description loaded from: "
        f"{JOB_DESCRIPTION_FILE}"
    )

    # --------------------------------------------------
    # 3. Ingest resumes
    # --------------------------------------------------

    print("\n[3/7] Ingesting resumes...")

    resumes = ingest_resumes()

    print(
        f"Resumes discovered: {len(resumes)}"
    )

    if not resumes:

        print("No resumes found.")

        save_json(
            "final_run.json",
            {
                "status": "no_resumes",
                "processed": [],
                "failed": []
            }
        )

        return

    # --------------------------------------------------
    # 4. Duplicate detection
    # --------------------------------------------------

    print("\n[4/7] Checking duplicate resumes...")

    resumes = detect_duplicate_files(resumes)

    unique_resumes = [
        resume
        for resume in resumes
        if not resume.get("is_duplicate", False)
    ]

    duplicates = [
        resume
        for resume in resumes
        if resume.get("is_duplicate", False)
    ]

    print(
        f"Unique resumes: {len(unique_resumes)}"
    )

    print(
        f"Duplicate resumes: {len(duplicates)}"
    )

    # --------------------------------------------------
    # 5. AI candidate processing
    # --------------------------------------------------

    print("\n[5/7] Running AI candidate evaluation...")

    graph = build_candidate_graph()

    if MAX_CANDIDATES is not None:

        unique_resumes = unique_resumes[
            :MAX_CANDIDATES
        ]

    successful_candidates = []
    failed_candidates = []

    for index, resume in enumerate(
        unique_resumes,
        start=1
    ):

        print("\n----------------------------------------")
        print(
            f"Candidate {index}/"
            f"{len(unique_resumes)}"
        )
        print(
            f"File: {resume['filename']}"
        )
        print("----------------------------------------")

        try:

            result = process_candidate(
                graph=graph,
                resume=resume,
                job_description=job_description
            )

            error = result.get("error")

            if error:

                print(
                    f"ERROR: {error}"
                )

                failed_candidates.append({
                    "filename": resume["filename"],
                    "error": error
                })

                continue

            evaluation = result.get(
                "evaluation"
            )

            critic_result = result.get(
                "critic_result"
            )

            scores = result.get(
                "scores"
            )

            if evaluation is None:

                error = (
                    "No candidate evaluation "
                    "was produced."
                )

                print(
                    f"ERROR: {error}"
                )

                failed_candidates.append({
                    "filename": resume["filename"],
                    "error": error
                })

                continue

            print(
                f"Candidate: "
                f"{evaluation.candidate_name}"
            )

            print(
                f"Overall Score: "
                f"{scores['overall_score']}"
            )

            if critic_result:

                print(
                    f"Critic Passed: "
                    f"{critic_result.passed}"
                )

            successful_candidates.append({
                "filename": resume["filename"],
                "candidate_name": (
                    evaluation.candidate_name
                ),
                "evaluation": serialize_evaluation(
                    evaluation
                ),
                "critic": serialize_critic(
                    critic_result
                ),
                "scores": scores
            })

        except Exception as error:

            print(
                f"ERROR processing "
                f"{resume['filename']}: "
                f"{error}"
            )

            failed_candidates.append({
                "filename": resume["filename"],
                "error": str(error)
            })

    # --------------------------------------------------
    # Save AI results
    # --------------------------------------------------

    save_json(
        "candidate_evaluations.json",
        successful_candidates
    )

    # --------------------------------------------------
    # 6. Ranking and shortlist
    # --------------------------------------------------

    print("\n[6/7] Ranking candidates...")

    ranked_candidates = rank_candidates()

    print_ranking(
        ranked_candidates
    )

    shortlisted_candidates = get_top_candidates(
        percentage=0.05
    )

    print_shortlist(
        shortlisted_candidates
    )

    save_json(
        "ranking.json",
        ranked_candidates
    )

    # --------------------------------------------------
    # Interview drafts
    # --------------------------------------------------

    interview_drafts = create_interview_drafts(
        shortlisted_candidates
    )

    print_interview_queue(
        interview_drafts
    )

    save_json(
        "interview_drafts.json",
        interview_drafts
    )

    # --------------------------------------------------
    # 7. Human approval
    # --------------------------------------------------

    print("\n[7/7] Human approval...")

    approval_results = []

    for draft in interview_drafts:

        decision = request_human_approval(
            draft
        )

        candidate_id = draft[
            "candidate_id"
        ]

        if decision == "approved":

            update_candidate_status(
                candidate_id,
                "approved"
            )

        elif decision == "rejected":

            update_candidate_status(
                candidate_id,
                "rejected"
            )

        approval_results.append({
            "candidate_id": candidate_id,
            "candidate_name": (
                draft["candidate_name"]
            ),
            "decision": decision
        })

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    final_run = {

        "status": "completed",

        "resumes_discovered": len(resumes),

        "unique_resumes": len(unique_resumes),

        "duplicates": [
            {
                "filename": resume["filename"],
                "duplicate_of": resume.get(
                    "duplicate_of"
                )
            }
            for resume in duplicates
        ],

        "successful_candidates": (
            successful_candidates
        ),

        "failed_candidates": (
            failed_candidates
        ),

        "ranking": ranked_candidates,

        "shortlist": (
            shortlisted_candidates
        ),

        "interview_drafts": (
            interview_drafts
        ),

        "approval_results": (
            approval_results
        )
    }

    final_path = save_json(
        "final_run.json",
        final_run
    )

    print("\n========================================")
    print("FINAL RUN SUMMARY")
    print("========================================")

    print(
        f"Resumes discovered: "
        f"{len(resumes)}"
    )

    print(
        f"Unique resumes: "
        f"{len(unique_resumes)}"
    )

    print(
        f"Duplicates: "
        f"{len(duplicates)}"
    )

    print(
        f"Successful evaluations: "
        f"{len(successful_candidates)}"
    )

    print(
        f"Failed evaluations: "
        f"{len(failed_candidates)}"
    )

    print(
        f"Ranked candidates: "
        f"{len(ranked_candidates)}"
    )

    print(
        f"Shortlisted candidates: "
        f"{len(shortlisted_candidates)}"
    )

    print(
        f"Interview drafts: "
        f"{len(interview_drafts)}"
    )

    print(
        f"Approval decisions: "
        f"{len(approval_results)}"
    )

    print(
        f"\nResults saved to: "
        f"{final_path}"
    )

    print("\n========================================")
    print("DEMO COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()