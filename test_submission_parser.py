from submission_parser import parse_submission
from tally_service import get_submission

FORM_ID = "obJN25"
SUBMISSION_ID = "gbrAe9l"


submission = get_submission(
    form_id=FORM_ID,
    submission_id=SUBMISSION_ID
)

answers = parse_submission(submission)

print("=" * 70)
print("PARSED ANSWERS")
print("=" * 70)

for question_id, answer in answers.items():
    print(
        f"{question_id} -> {answer}"
    )

print("=" * 70)