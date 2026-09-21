import json

from tally_service import get_submission

FORM_ID = "obJN25"
SUBMISSION_ID = "gbrAe9l"


print("=" * 70)
print("SINGLE TALLY SUBMISSION TEST")
print("=" * 70)

result = get_submission(
    form_id=FORM_ID,
    submission_id=SUBMISSION_ID
)

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

print("=" * 70)