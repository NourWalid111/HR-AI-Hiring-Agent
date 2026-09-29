from pathlib import Path
from pypdf import PdfReader
from docx import Document
import hashlib


RESUME_DIR = Path("resumes")


def read_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))

    text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return text.strip()


def read_docx(file_path: Path) -> str:
    document = Document(str(file_path))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def read_txt(file_path: Path) -> str:
    return file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def ingest_resumes() -> list[dict]:
    RESUME_DIR.mkdir(exist_ok=True)

    resumes = []

    for file_path in RESUME_DIR.iterdir():

        if not file_path.is_file():
            continue

        try:

            if file_path.suffix.lower() == ".pdf":
                text = read_pdf(file_path)

            elif file_path.suffix.lower() == ".docx":
                text = read_docx(file_path)

            elif file_path.suffix.lower() == ".txt":
                text = read_txt(file_path)

            else:
                continue

            resumes.append({
                "filename": file_path.name,
                "path": str(file_path),
                "text": text
            })

        except Exception as e:

            resumes.append({
                "filename": file_path.name,
                "path": str(file_path),
                "text": "",
                "error": str(e)
            })

    return resumes
def calculate_file_hash(file_path: str) -> str:

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(4096),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()
def detect_duplicate_files(
    resumes: list[dict]
) -> list[dict]:

    seen_hashes = {}

    results = []

    for resume in resumes:

        file_hash = calculate_file_hash(
            resume["path"]
        )

        duplicate_of = seen_hashes.get(file_hash)

        result = {
            **resume,
            "file_hash": file_hash,
            "is_duplicate": duplicate_of is not None,
            "duplicate_of": duplicate_of
        }

        results.append(result)

        if duplicate_of is None:
            seen_hashes[file_hash] = resume["filename"]

    return results