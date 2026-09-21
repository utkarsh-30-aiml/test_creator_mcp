from database import get_connection

TALLY_FORM_ID = "819b5x"


connection = get_connection()
cursor = connection.cursor()


# ---------------------------------------------------------
# GET TEST
# ---------------------------------------------------------

cursor.execute(
    """
    SELECT
        id,
        tally_form_id,
        title,
        description,
        created_at
    FROM tests
    WHERE tally_form_id = %s;
    """,
    (TALLY_FORM_ID,)
)

test = cursor.fetchone()


print("=" * 70)
print("DATABASE TEST VERIFICATION")
print("=" * 70)


if not test:
    print("❌ Test not found in database.")

else:

    print("✓ Test found")
    print(f"Database ID : {test[0]}")
    print(f"Tally ID    : {test[1]}")
    print(f"Title       : {test[2]}")
    print(f"Description : {test[3]}")
    print(f"Created At  : {test[4]}")


    # -----------------------------------------------------
    # GET QUESTIONS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            question_id,
            tally_question_id,
            question,
            correct_answer,
            marks,
            negative_marks
        FROM questions
        WHERE test_id = %s
        ORDER BY question_id;
        """,
        (test[0],)
    )

    questions = cursor.fetchall()


    print("\n" + "=" * 70)
    print("QUESTIONS")
    print("=" * 70)


    for question in questions:

        print(
            f"Q{question[0]}"
        )

        print(
            f"  Tally Question ID : {question[1]}"
        )

        print(
            f"  Question          : {question[2]}"
        )

        print(
            f"  Correct Answer    : {question[3]}"
        )

        print(
            f"  Marks             : {question[4]}"
        )

        print(
            f"  Negative Marks    : {question[5]}"
        )

        print("-" * 70)


cursor.close()
connection.close()