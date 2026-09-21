from tally_service import get_form_submissions

FORM_ID = "PdoJdB"


submissions = get_form_submissions(
    FORM_ID
)

print("Response type:", type(submissions))
print("\nFull response:")
print(submissions)