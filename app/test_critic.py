from app.agents import (
    evaluate_candidate,
    critique_candidate
)

from app.tools import ingest_resumes


def main():

    resumes = ingest_resumes()

    resume = resumes[0]

    with open(
        "job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:
        job_description = file.read()

    print("\n==============================")
    print("EVALUATING CANDIDATE")
    print("==============================")

    evaluation = evaluate_candidate(
        resume_text=resume["text"],
        job_description=job_description
    )

    print(evaluation.model_dump_json(indent=2))

    print("\n==============================")
    print("RUNNING EVIDENCE CRITIC")
    print("==============================")

    critique = critique_candidate(
        resume_text=resume["text"],
        evaluation=evaluation
    )

    print(critique.model_dump_json(indent=2))


if __name__ == "__main__":
    main()