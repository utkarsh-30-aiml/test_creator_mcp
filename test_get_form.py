import json

from tally_service import get_form

FORM_ID = "zxVBd1"


print("=" * 70)
print("TALLY FORM TEST")
print("=" * 70)

result = get_form(FORM_ID)

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

print("=" * 70)