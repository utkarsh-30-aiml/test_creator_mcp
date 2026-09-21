from test_repository import save_submission

FORM_ID = "819b5x"
SUBMISSION_ID = "TEST_SUBMISSION_001"
SUBMITTED_AT = "2026-09-21 20:00:00"


submission_db_id = save_submission(
    tally_form_id=FORM_ID,
    tally_submission_id=SUBMISSION_ID,
    submitted_at=SUBMITTED_AT
)

print("Submission saved successfully.")
print("Database submission ID:", submission_db_id)