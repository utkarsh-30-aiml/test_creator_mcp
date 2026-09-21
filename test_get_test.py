from test_repository import get_test_by_tally_form_id

TALLY_FORM_ID = "819b5x"


test, question_mapping = get_test_by_tally_form_id(
    TALLY_FORM_ID
)


print("=" * 70)
print("RETRIEVED TEST")
print("=" * 70)

print(f"Title       : {test.title}")
print(f"Description : {test.description}")
print(
    f"Questions   : {len(test.questions)}"
)


print("\n" + "=" * 70)
print("QUESTIONS")
print("=" * 70)


for question in test.questions:

    print(
        f"Q{question.id}: "
        f"{question.question}"
    )

    print(
        f"  Correct answer : "
        f"{question.correct_answer}"
    )

    print(
        f"  Marks          : "
        f"{question.marks}"
    )

    print(
        f"  Negative marks : "
        f"{question.negative_marks}"
    )


print("\n" + "=" * 70)
print("QUESTION MAPPING")
print("=" * 70)


for question_id, tally_question_id in question_mapping.items():

    print(
        f"Q{question_id} -> "
        f"{tally_question_id}"
    )