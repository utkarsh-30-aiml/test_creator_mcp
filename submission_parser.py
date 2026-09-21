def parse_submission(
    submission: dict,
    question_mapping: dict[int, str]
) -> dict[int, str | None]:
    """
    Convert Tally submission responses into:

    {
        our_question_id: selected_answer
    }

    question_mapping:
    {
        our_question_id: tally_question_id
    }
    """

    submission_data = submission.get("submission")

    if not submission_data:
        raise ValueError("Submission data not found.")

    responses = submission_data.get("responses", [])

    # Reverse mapping:
    # Tally question ID -> our question ID
    reverse_mapping = {
        tally_question_id: question_id
        for question_id, tally_question_id
        in question_mapping.items()
    }

    parsed_answers = {}

    for response in responses:

        tally_question_id = response.get("questionId")
        answers = response.get("answer", [])

        if not tally_question_id:
            continue

        question_id = reverse_mapping.get(
            tally_question_id
        )

        if question_id is None:
            continue

        if not answers:
            parsed_answers[question_id] = None
        else:
            parsed_answers[question_id] = answers[0]

    return parsed_answers