from app.tools import (
    ingest_resumes,
    detect_duplicate_files
)


def main():

    resumes = ingest_resumes()

    resumes = detect_duplicate_files(resumes)

    print(f"Found {len(resumes)} resumes.")

    for resume in resumes:

        print("\n-------------------------")
        print("FILE:", resume["filename"])

        print(
            "Duplicate:",
            resume["is_duplicate"]
        )

        if resume["is_duplicate"]:

            print(
                "Duplicate of:",
                resume["duplicate_of"]
            )


if __name__ == "__main__":
    main()