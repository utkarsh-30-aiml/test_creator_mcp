from test_repository import save_result

SUBMISSION_ID = "TEST_SUBMISSION_001"

evaluation_result = {
    "total_score": 0.67,
    "correct": 1,
    "incorrect": 1,
    "unanswered": 0,
    "total_questions": 2,
    "results": [
        {
            "question_id": 1,
            "student_answer": "C. 20 bits",
            "correct_answer": "B",
            "status": "incorrect",
            "marks": -0.33,
            "explanation": "4 KB = 2^12 bytes, so 12 bits are required for the page offset."
        },
        {
            "question_id": 2,
            "student_answer": "A. Page table",
            "correct_answer": "A",
            "status": "correct",
            "marks": 1.0,
            "explanation": "A page table maps logical pages to physical memory frames."
        }
    ]
}


result_id = save_result(
    tally_submission_id=SUBMISSION_ID,
    evaluation_result=evaluation_result
)

print("Result saved successfully.")
print("Database result ID:", result_id)