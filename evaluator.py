from schemas import Test


def evaluate_test(
    test: Test,
    answers: dict[int, str | None]
) -> dict:

    results = []
    wrong_questions = []

    total_score = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    for question in test.questions:

        student_answer = answers.get(question.id)

        if not student_answer:

            status = "unanswered"
            marks_obtained = 0.0
            unanswered_count += 1

        elif student_answer.startswith(
            question.correct_answer + "."
        ):

            status = "correct"
            marks_obtained = question.marks
            correct_count += 1

        else:

            status = "incorrect"
            marks_obtained = -question.negative_marks
            incorrect_count += 1

        total_score += marks_obtained

        result = {
            "question_id": question.id,
            "subject": question.subject,
            "topic": question.topic,
            "question": question.question,
            "options": question.options,
            "student_answer": student_answer,
            "correct_answer": question.correct_answer,
            "status": status,
            "marks": marks_obtained,
            "explanation": question.explanation,
            "source_url": question.source_url,
        }

        results.append(result)

        # Keep complete details of questions answered incorrectly
        if status == "incorrect":
            wrong_questions.append(result)

    return {
        "total_score": round(total_score, 2),
        "correct": correct_count,
        "incorrect": incorrect_count,
        "unanswered": unanswered_count,
        "total_questions": len(test.questions),
        "results": results,
        "wrong_questions": wrong_questions,
    }