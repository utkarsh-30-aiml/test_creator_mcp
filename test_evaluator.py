from evaluator import evaluate_test
from schemas import Test

test_data = {
    "title": "GATE CSE - Evaluation Test",
    "description": "Evaluation test",
    "questions": [
        {
            "id": 1,
            "subject": "OS",
            "topic": "Paging",
            "type": "MCQ",
            "question": "What is the size of a 4 KB page offset?",
            "options": {
                "A": "10 bits",
                "B": "12 bits",
                "C": "16 bits",
                "D": "20 bits"
            },
            "correct_answer": "B",
            "explanation": "4 KB = 2^12 bytes.",
            "marks": 1,
            "negative_marks": 0.33,
            "source_url": None
        },
        {
            "id": 2,
            "subject": "OS",
            "topic": "Paging",
            "type": "MCQ",
            "question": "Which maps pages to frames?",
            "options": {
                "A": "Page table",
                "B": "Stack",
                "C": "Queue",
                "D": "Heap"
            },
            "correct_answer": "A",
            "explanation": "The page table maps pages to frames.",
            "marks": 1,
            "negative_marks": 0.33,
            "source_url": None
        },
        {
            "id": 3,
            "subject": "OS",
            "topic": "Memory",
            "type": "MCQ",
            "question": "Which is volatile memory?",
            "options": {
                "A": "RAM",
                "B": "ROM",
                "C": "SSD",
                "D": "HDD"
            },
            "correct_answer": "A",
            "explanation": "RAM is volatile memory.",
            "marks": 1,
            "negative_marks": 0.33,
            "source_url": None
        }
    ]
}


test = Test(**test_data)


# Tally question IDs
question_mapping = {
    1: "xNQrbd",
    2: "ZRV8kV",
    3: "fake-question-id"
}


# Simulate student answers
answers = {
    1: "C. 20 bits",
    2: "A. Page table",
    3: None
}


result = evaluate_test(
    test=test,
    answers=answers
)


print("=" * 70)
print("EVALUATION RESULT")
print("=" * 70)

print(f"Total Score : {result['total_score']}")
print(f"Correct     : {result['correct']}")
print(f"Incorrect   : {result['incorrect']}")
print(f"Unanswered  : {result['unanswered']}")

print()

for item in result["results"]:

    print(
        f"Q{item['question_id']} "
        f"-> {item['status']} "
        f"-> {item['marks']}"
    )

print("=" * 70)