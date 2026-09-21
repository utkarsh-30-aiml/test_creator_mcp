from evaluator import evaluate_test
from submission_parser import parse_submission
from tally_service import get_submission
from test_repository import get_test_by_tally_form_id, save_result, save_submission

FORM_ID = "819b5x"
SUBMISSION_ID = "EqY0JOl"

# --------------------------------------------------
# 1. Get submission from Tally
# --------------------------------------------------

submission = get_submission(
    FORM_ID,
    SUBMISSION_ID
)

print("✓ Submission fetched from Tally")


# --------------------------------------------------
# 2. Load test + question mapping from PostgreSQL
# --------------------------------------------------

test, question_mapping = get_test_by_tally_form_id(
    FORM_ID
)

print("✓ Test loaded from PostgreSQL")

print("Title:", test.title)
print("Questions:", len(test.questions))

print("Question mapping:")
print(question_mapping)


# --------------------------------------------------
# 3. Parse Tally answers
# --------------------------------------------------

answers = parse_submission(
    submission,
    question_mapping
)

print("\n✓ Submission parsed")
print("Answers:")
print(answers)


# --------------------------------------------------
# 4. Evaluate
# --------------------------------------------------

evaluation_result = evaluate_test(
    test,
    answers
)

print("\n✓ Test evaluated")
print(evaluation_result)


# --------------------------------------------------
# 5. Save submission
# --------------------------------------------------

submission_db_id = save_submission(
    tally_form_id=FORM_ID,
    tally_submission_id=SUBMISSION_ID,
    submitted_at=submission["submission"].get(
        "submittedAt"
    )
)

print("\n✓ Submission saved")
print("Submission DB ID:", submission_db_id)


# --------------------------------------------------
# 6. Save result
# --------------------------------------------------

result_db_id = save_result(
    tally_submission_id=SUBMISSION_ID,
    evaluation_result=evaluation_result
)

print("\n✓ Result saved")
print("Result DB ID:", result_db_id)