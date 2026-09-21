from schemas import Question, Test
from test_repository import save_test

test = Test(
    title="GATE CSE - Database Test",
    description="Testing database persistence.",
    questions=[
        Question(
            id=1,
            subject="DBMS",
            topic="Normalization",
            type="MCQ",
            question="Which normal form removes partial dependency?",
            options={
                "A": "1NF",
                "B": "2NF",
                "C": "3NF",
                "D": "BCNF"
            },
            correct_answer="B",
            explanation=(
                "2NF removes partial dependency "
                "on a composite key."
            ),
            marks=1,
            negative_marks=0.33
        ),
        Question(
            id=2,
            subject="DBMS",
            topic="Transactions",
            type="MCQ",
            question="Which property ensures atomicity?",
            options={
                "A": "ACID",
                "B": "CAP",
                "C": "BASE",
                "D": "CRUD"
            },
            correct_answer="A",
            explanation=(
                "Atomicity is one of the ACID properties."
            ),
            marks=1,
            negative_marks=0.33
        )
    ]
)


question_mapping = {
    1: "TEST_TALLY_Q1",
    2: "TEST_TALLY_Q2"
}


test_db_id = save_test(
    test=test,
    tally_form_id="TEST_FORM_001",
    question_mapping=question_mapping
)


print("=" * 70)
print("SAVE TEST")
print("=" * 70)

print("✓ Test saved")
print(f"Database test ID: {test_db_id}")