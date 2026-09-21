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
        our_question_id: Tally blockGroupUuid
    }
    """

    submission_data = submission.get("submission")

    if not submission_data:
        raise ValueError("Submission data not found.")

    responses = submission_data.get(
        "responses",
        []
    )

    tally_questions = submission.get(
        "questions",
        []
    )

    # ---------------------------------------------
    # Build:
    #
    # Tally question ID
    #        ↓
    # Tally blockGroupUuid
    # ---------------------------------------------

    question_id_to_group_uuid = {}

    for question in tally_questions:

        tally_question_id = question.get("id")

        fields = question.get(
            "fields",
            []
        )

        for field in fields:

            block_group_uuid = field.get(
                "blockGroupUuid"
            )

            if tally_question_id and block_group_uuid:

                question_id_to_group_uuid[
                    tally_question_id
                ] = block_group_uuid

    # ---------------------------------------------
    # Build reverse mapping:
    #
    # Tally blockGroupUuid
    #        ↓
    # Our question ID
    # ---------------------------------------------

    group_uuid_to_question_id = {
        tally_group_uuid: question_id
        for question_id, tally_group_uuid
        in question_mapping.items()
    }

    parsed_answers = {}

    # ---------------------------------------------
    # Parse submitted answers
    # ---------------------------------------------

    for response in responses:

        tally_question_id = response.get(
            "questionId"
        )

        answers = response.get(
            "answer",
            []
        )

        if not tally_question_id:
            continue

        block_group_uuid = (
            question_id_to_group_uuid.get(
                tally_question_id
            )
        )

        if not block_group_uuid:
            continue

        question_id = (
            group_uuid_to_question_id.get(
                block_group_uuid
            )
        )

        if question_id is None:
            continue

        if not answers:
            parsed_answers[question_id] = None
        else:
            parsed_answers[question_id] = answers[0]

    return parsed_answers