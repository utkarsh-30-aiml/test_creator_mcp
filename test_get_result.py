from test_repository import get_result_by_submission_id

SUBMISSION_ID = "EqY0JOl"


result = get_result_by_submission_id(
    SUBMISSION_ID
)

print("Result retrieved successfully.")

print("Result ID:", result["result_id"])
print("Submission DB ID:", result["submission_id"])
print("Total Score:", result["total_score"])
print("Correct:", result["correct"])
print("Incorrect:", result["incorrect"])
print("Unanswered:", result["unanswered"])
print("Total Questions:", result["total_questions"])

print("\nComplete result:")
print(result["result"])