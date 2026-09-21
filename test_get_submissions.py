from tally_service import get_form_submissions


FORM_ID = "819b5x"


submissions = get_form_submissions(
    FORM_ID
)

print("Response type:", type(submissions))
print("\nFull response:")
print(submissions)