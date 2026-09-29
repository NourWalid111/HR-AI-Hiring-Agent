from app.agents import evaluate_candidate
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
    print("GEMINI SINGLE-CANDIDATE TEST")
    print("==============================")

    print(
        f"Resume: {resume['filename']}"
    )

    evaluation = evaluate_candidate(
        resume_text=resume["text"],
        job_description=job_description
    )

    print("\n==============================")
    print("EVALUATION SUCCESSFUL")
    print("==============================")

    print(
        evaluation.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()