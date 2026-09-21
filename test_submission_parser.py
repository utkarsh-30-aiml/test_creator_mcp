from submission_parser import parse_submission
from tally_service import get_submission
from test_repository import get_test_by_tally_form_id

FORM_ID = "819b5x"
SUBMISSION_ID = "EqY0JOl"


# Get real submission from Tally
submission = get_submission(
    FORM_ID,
    SUBMISSION_ID
)

print("✓ Submission fetched")


# Get test + mapping from PostgreSQL
test, question_mapping = get_test_by_tally_form_id(
    FORM_ID
)

print("✓ Test loaded")

print("Question mapping:")
print(question_mapping)


# Parse answers
answers = parse_submission(
    submission,
    question_mapping
)

print("\nParsed answers:")
print(answers)