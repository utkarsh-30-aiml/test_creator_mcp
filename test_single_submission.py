import json

from evaluator import evaluate_test
from schemas import Question, Test
from submission_parser import parse_submission
from tally_service import get_submission

FORM_ID = "RGOelP"
SUBMISSION_ID = "WJdoDNP"


# ---------------------------------------------------------
# ORIGINAL TEST
# ---------------------------------------------------------

test = Test(
    title="GATE CSE - Paging Test",
    description="Practice test on Operating Systems - Paging.",
    questions=[
        Question(
            id=1,
            subject="Operating Systems",
            topic="Paging",
            type="MCQ",
            question=(
                "Consider a system with 32-bit logical addresses "
                "and a 4 KB page size. How many bits are required "
                "for the page offset?"
            ),
            options={
                "A": "10 bits",
                "B": "12 bits",
                "C": "20 bits",
                "D": "32 bits"
            },
            correct_answer="B",
            explanation=(
                "4 KB = 2^12 bytes, so 12 bits are required "
                "for the page offset."
            ),
            marks=1,
            negative_marks=0.33
        ),

        Question(
            id=2,
            subject="Operating Systems",
            topic="Paging",
            type="MCQ",
            question=(
                "Which data structure is used to map logical "
                "pages to physical frames?"
            ),
            options={
                "A": "Page table",
                "B": "Stack",
                "C": "Queue",
                "D": "Heap"
            },
            correct_answer="A",
            explanation=(
                "A page table maps logical pages to physical "
                "memory frames."
            ),
            marks=1,
            negative_marks=0.33
        )
    ]
)


# ---------------------------------------------------------
# TALLY QUESTION MAPPING
# ---------------------------------------------------------

question_mapping = {
    1: "ZRVag0",
    2: "NBVogG"
}


# ---------------------------------------------------------
# STEP 1: GET SUBMISSION
# ---------------------------------------------------------

print("=" * 70)
print("MANUAL END-TO-END TEST")
print("=" * 70)

print("\n[1] Fetching Tally submission...")

submission = get_submission(
    form_id=FORM_ID,
    submission_id=SUBMISSION_ID
)

print("✓ Submission fetched")


# ---------------------------------------------------------
# STEP 2: PARSE SUBMISSION
# ---------------------------------------------------------

print("\n[2] Parsing submission...")

answers = parse_submission(
    submission=submission,
    question_mapping=question_mapping
)

print("✓ Submission parsed")

print("\nParsed answers:")

for question_id, answer in answers.items():
    print(
        f"Q{question_id} -> {answer}"
    )


# ---------------------------------------------------------
# STEP 3: EVALUATE
# ---------------------------------------------------------

print("\n[3] Evaluating test...")

result = evaluate_test(
    test=test,
    answers=answers
)

print("✓ Evaluation completed")


# ---------------------------------------------------------
# STEP 4: FINAL RESULT
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("EVALUATED TEST RESULT")
print("=" * 70)

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

print("=" * 70)