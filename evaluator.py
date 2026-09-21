from schemas import Test


def evaluate_test(
    test: Test,
    answers: dict[str, str],
    question_mapping: dict[int, str]
) -> dict:
    """
    Evaluate a submitted GATE test.

    Parameters
    ----------
    test:
        Original Test object containing questions
        and correct answers.

    answers:
        Mapping of Tally question IDs to submitted
        answers.

    question_mapping:
        Mapping from our question IDs to Tally
        question IDs.

        Example:
        {
            1: "xNQrbd",
            2: "ZRV8kV"
        }
    """

    results = []

    total_score = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    for question in test.questions:

        tally_question_id = question_mapping.get(
            question.id
        )

        # ---------------------------------------------
        # No mapping found
        # ---------------------------------------------

        if not tally_question_id:

            raise ValueError(
                f"No Tally question mapping found "
                f"for question ID {question.id}"
            )

        # ---------------------------------------------
        # Student answer
        # ---------------------------------------------

        student_answer = answers.get(
            tally_question_id
        )

        # ---------------------------------------------
        # Unanswered
        # ---------------------------------------------

        if not student_answer:

            status = "unanswered"
            marks_obtained = 0.0

            unanswered_count += 1

        # ---------------------------------------------
        # Correct
        # ---------------------------------------------

        elif student_answer.startswith(
            question.correct_answer + "."
        ):

            status = "correct"
            marks_obtained = question.marks

            correct_count += 1

        # ---------------------------------------------
        # Incorrect
        # ---------------------------------------------

        else:

            status = "incorrect"
            marks_obtained = -question.negative_marks

            incorrect_count += 1

        total_score += marks_obtained

        results.append(
            {
                "question_id": question.id,
                "tally_question_id": tally_question_id,
                "student_answer": student_answer,
                "correct_answer": question.correct_answer,
                "status": status,
                "marks": marks_obtained,
                "explanation": question.explanation
            }
        )

    return {
        "total_score": round(total_score, 2),
        "correct": correct_count,
        "incorrect": incorrect_count,
        "unanswered": unanswered_count,
        "total_questions": len(test.questions),
        "results": results
    }