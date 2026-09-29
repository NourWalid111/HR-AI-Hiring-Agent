import sqlite3
from datetime import datetime


DATABASE_NAME = "hr_agent.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Enable foreign-key enforcement
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,

            relevant_experience_years REAL,

            required_score REAL,
            experience_score REAL,
            preferred_score REAL,
            background_score REAL,
            overall_score REAL,

            status TEXT DEFAULT 'evaluated',

            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            skill TEXT NOT NULL,
            category TEXT NOT NULL,

            score REAL NOT NULL,
            years_experience REAL NOT NULL,

            evidence TEXT NOT NULL,

            FOREIGN KEY(candidate_id)
                REFERENCES candidates(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def save_candidate(resume, evaluation, scores):

    connection = get_connection()
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    file_hash = resume["file_hash"]

    # Check whether this resume already exists
    cursor.execute("""
        SELECT id
        FROM candidates
        WHERE file_hash = ?
    """, (file_hash,))

    existing = cursor.fetchone()

    if existing:

        candidate_id = existing[0]

        # Update existing candidate
        cursor.execute("""
            UPDATE candidates
            SET
                candidate_name = ?,
                filename = ?,
                relevant_experience_years = ?,
                required_score = ?,
                experience_score = ?,
                preferred_score = ?,
                background_score = ?,
                overall_score = ?,
                status = ?,
                created_at = ?
            WHERE id = ?
        """, (
            evaluation.candidate_name,
            resume["filename"],
            evaluation.relevant_experience_years,
            scores["required_score"],
            scores["experience_score"],
            scores["preferred_score"],
            scores["background_score"],
            scores["overall_score"],
            "evaluated",
            datetime.now().isoformat(),
            candidate_id
        ))

        # Remove old skill evaluations
        cursor.execute("""
            DELETE FROM skill_evaluations
            WHERE candidate_id = ?
        """, (candidate_id,))

    else:

        # Insert new candidate
        cursor.execute("""
            INSERT INTO candidates (
                candidate_name,
                filename,
                file_hash,
                relevant_experience_years,
                required_score,
                experience_score,
                preferred_score,
                background_score,
                overall_score,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evaluation.candidate_name,
            resume["filename"],
            file_hash,
            evaluation.relevant_experience_years,
            scores["required_score"],
            scores["experience_score"],
            scores["preferred_score"],
            scores["background_score"],
            scores["overall_score"],
            "evaluated",
            datetime.now().isoformat()
        ))

        candidate_id = cursor.lastrowid

    # Insert current skill evaluations
    for skill in evaluation.skills:

        cursor.execute("""
            INSERT INTO skill_evaluations (
                candidate_id,
                skill,
                category,
                score,
                years_experience,
                evidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            skill.skill,
            skill.category,
            skill.score,
            skill.years_experience,
            skill.evidence
        ))

    connection.commit()
    connection.close()

    return candidate_id


def get_all_candidates():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM candidates
        ORDER BY overall_score DESC
    """)

    candidates = cursor.fetchall()

    connection.close()

    return candidates


def get_candidate_skills(candidate_id):

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM skill_evaluations
        WHERE candidate_id = ?
        ORDER BY score DESC
    """, (candidate_id,))

    skills = cursor.fetchall()

    connection.close()

    return skills


def update_candidate_status(
    candidate_id: int,
    status: str
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE candidates
        SET status = ?
        WHERE id = ?
    """, (
        status,
        candidate_id
    ))

    connection.commit()
    connection.close()


def archive_existing_candidates():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE candidates
        SET status = 'archived'
        WHERE status IN (
            'evaluated',
            'pending_approval'
        )
    """)

    connection.commit()
    connection.close()
   