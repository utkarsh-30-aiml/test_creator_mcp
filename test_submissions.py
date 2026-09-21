import json

from tally_service import get_form_submissions

FORM_ID = "RGOelP"


print("=" * 70)
print("TALLY SUBMISSION TEST")
print("=" * 70)

result = get_form_submissions(FORM_ID)

print(json.dumps(result, indent=2, ensure_ascii=False))

print("=" * 70)