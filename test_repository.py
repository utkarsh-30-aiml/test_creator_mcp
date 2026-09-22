from database import get_connection
from schemas import Question, Test
import json

def save_test(
    test: Test,
    tally_form_id: str,
    question_mapping: dict[int, str]
) -> int:

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # SAVE TEST
        # -----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO tests (
                tally_form_id,
                title,
                description
            )
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (
                tally_form_id,
                test.title,
                test.description
            )
        )

        test_db_id = cursor.fetchone()[0]

        # -----------------------------------------------------
        # SAVE QUESTIONS
        # -----------------------------------------------------

        for question in test.questions:

            tally_question_id = question_mapping.get(
                question.id
            )

            cursor.execute(
                """
                INSERT INTO questions (
                    test_id,
                    question_id,
                    tally_question_id,
                    question,
                    options,
                    correct_answer,
                    explanation,
                    marks,
                    negative_marks
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    test_db_id,
                    question.id,
                    tally_question_id,
                    question.question,
                    __import__("json").dumps(
                        question.options
                    ),
                    question.correct_answer,
                    question.explanation,
                    question.marks,
                    question.negative_marks
                )
            )

        connection.commit()

        return test_db_id

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()
        

def get_test_by_tally_form_id(
    tally_form_id: str
) -> tuple[Test, dict[int, str]]:

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # GET TEST
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                title,
                description
            FROM tests
            WHERE tally_form_id = %s;
            """,
            (tally_form_id,)
        )

        test_row = cursor.fetchone()

        if not test_row:
            raise ValueError(
                f"Test with Tally form ID "
                f"'{tally_form_id}' was not found."
            )

        database_test_id = test_row[0]
        title = test_row[1]
        description = test_row[2]

        # -----------------------------------------------------
        # GET QUESTIONS
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                question_id,
                tally_question_id,
                question,
                options,
                correct_answer,
                explanation,
                marks,
                negative_marks
            FROM questions
            WHERE test_id = %s
            ORDER BY question_id;
            """,
            (database_test_id,)
        )

        question_rows = cursor.fetchall()

        if not question_rows:
            raise ValueError(
                f"No questions found for test "
                f"'{tally_form_id}'."
            )

        questions = []

        question_mapping = {}

        for row in question_rows:

            (
                question_id,
                tally_question_id,
                question_text,
                options,
                correct_answer,
                explanation,
                marks,
                negative_marks
            ) = row

            questions.append(
                Question(
                    id=question_id,
                    subject="Unknown",
                    topic="Unknown",
                    type="MCQ",
                    question=question_text,
                    options=options,
                    correct_answer=correct_answer,
                    explanation=explanation,
                    marks=marks,
                    negative_marks=negative_marks
                )
            )

            question_mapping[
                question_id
            ] = tally_question_id

        # -----------------------------------------------------
        # BUILD TEST
        # -----------------------------------------------------

        test = Test(
            title=title,
            description=description,
            questions=questions
        )

        return test, question_mapping

    finally:

        cursor.close()
        connection.close()
        

def save_submission(
    tally_form_id: str,
    tally_submission_id: str,
    submitted_at
) -> int:

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ---------------------------------------------
        # Find the test
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM tests
            WHERE tally_form_id = %s;
            """,
            (tally_form_id,)
        )

        test_row = cursor.fetchone()

        if not test_row:
            raise ValueError(
                f"Test with Tally form ID "
                f"'{tally_form_id}' was not found."
            )

        test_id = test_row[0]

        # ---------------------------------------------
        # Check whether submission already exists
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM submissions
            WHERE tally_submission_id = %s;
            """,
            (tally_submission_id,)
        )

        existing_submission = cursor.fetchone()

        if existing_submission:
            return existing_submission[0]

        # ---------------------------------------------
        # Insert submission
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO submissions (
                test_id,
                tally_submission_id,
                submitted_at
            )
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (
                test_id,
                tally_submission_id,
                submitted_at
            )
        )

        submission_db_id = cursor.fetchone()[0]

        connection.commit()

        return submission_db_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
        
def save_result(
    tally_submission_id: str,
    evaluation_result: dict
) -> int:

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ---------------------------------------------
        # Find submission
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM submissions
            WHERE tally_submission_id = %s;
            """,
            (tally_submission_id,)
        )

        submission_row = cursor.fetchone()

        if not submission_row:
            raise ValueError(
                f"Submission with Tally submission ID "
                f"'{tally_submission_id}' was not found."
            )

        submission_id = submission_row[0]

        # ---------------------------------------------
        # Check whether result already exists
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM results
            WHERE submission_id = %s;
            """,
            (submission_id,)
        )

        existing_result = cursor.fetchone()

        if existing_result:
            return existing_result[0]

        # ---------------------------------------------
        # Insert result
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO results (
                submission_id,
                total_score,
                correct,
                incorrect,
                unanswered,
                total_questions,
                result_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                submission_id,
                evaluation_result["total_score"],
                evaluation_result["correct"],
                evaluation_result["incorrect"],
                evaluation_result["unanswered"],
                evaluation_result["total_questions"],
                __import__("json").dumps(
                    evaluation_result
                )
            )
        )

        result_id = cursor.fetchone()[0]

        connection.commit()

        return result_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
        

def get_result_by_submission_id(
    tally_submission_id: str
) -> dict:

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                r.id,
                r.submission_id,
                r.total_score,
                r.correct,
                r.incorrect,
                r.unanswered,
                r.total_questions,
                r.result_json,
                r.created_at
            FROM results r
            JOIN submissions s
                ON r.submission_id = s.id
            WHERE s.tally_submission_id = %s;
            """,
            (tally_submission_id,)
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                f"Result for Tally submission ID "
                f"'{tally_submission_id}' was not found."
            )

        (
            result_id,
            submission_id,
            total_score,
            correct,
            incorrect,
            unanswered,
            total_questions,
            result_json,
            created_at
        ) = row

        return {
    "result_id": result_id,
    "submission_id": submission_id,
    "total_score": total_score,
    "correct": correct,
    "incorrect": incorrect,
    "unanswered": unanswered,
    "total_questions": total_questions,
    "result": result_json,
    "created_at": created_at.isoformat()
        if created_at
        else None
}

    finally:
        cursor.close()
        connection.close()