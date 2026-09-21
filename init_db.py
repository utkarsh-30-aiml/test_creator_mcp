from database import get_connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # ---------------------------------------------------------
    # TESTS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id SERIAL PRIMARY KEY,
            tally_form_id VARCHAR(50) UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # QUESTIONS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            test_id INTEGER NOT NULL
                REFERENCES tests(id)
                ON DELETE CASCADE,

            question_id INTEGER NOT NULL,

            tally_question_id VARCHAR(50),

            question TEXT NOT NULL,

            options JSONB NOT NULL,

            correct_answer VARCHAR(1) NOT NULL,

            explanation TEXT NOT NULL,

            marks DOUBLE PRECISION NOT NULL,

            negative_marks DOUBLE PRECISION NOT NULL,

            UNIQUE(test_id, question_id)
        );
    """)

    # ---------------------------------------------------------
    # SUBMISSIONS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,

            test_id INTEGER NOT NULL
                REFERENCES tests(id)
                ON DELETE CASCADE,

            tally_submission_id VARCHAR(50) UNIQUE NOT NULL,

            submitted_at TIMESTAMP,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,

            submission_id INTEGER NOT NULL
                REFERENCES submissions(id)
                ON DELETE CASCADE,

            total_score DOUBLE PRECISION NOT NULL,

            correct INTEGER NOT NULL,

            incorrect INTEGER NOT NULL,

            unanswered INTEGER NOT NULL,

            total_questions INTEGER NOT NULL,

            result_json JSONB NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("=" * 70)
    print("DATABASE INITIALIZATION")
    print("=" * 70)
    print("✓ tests table created")
    print("✓ questions table created")
    print("✓ submissions table created")
    print("✓ results table created")
    print("✓ Database initialization completed")


if __name__ == "__main__":
    init_db()