from fastmcp import FastMCP

from evaluator import evaluate_test
from schemas import Test
from submission_parser import parse_submission
from tally_service import create_test_form, get_submission
from test_repository import (
    get_result_by_submission_id,
    get_test_by_tally_form_id,
    save_result,
    save_submission,
    save_test,
)

mcp = FastMCP("GATE Test Creator")


@mcp.tool()
def create_test(test: dict) -> dict:

    # ---------------------------------------------------------
    # 1. Validate test
    # ---------------------------------------------------------

    validated_test = Test(**test)

    # ---------------------------------------------------------
    # 2. Create Tally form
    # ---------------------------------------------------------

    result = create_test_form(
        validated_test
    )

    tally_form_id = result["id"]

    question_mapping = result["question_mapping"]

    # ---------------------------------------------------------
    # 3. Save test in database
    # ---------------------------------------------------------

    database_test_id = save_test(
        test=validated_test,
        tally_form_id=tally_form_id,
        question_mapping=question_mapping
    )

    # ---------------------------------------------------------
    # 4. Return result
    # ---------------------------------------------------------

    form_url = (
        f"https://tally.so/r/{tally_form_id}"
    )

    return {
        "success": True,
        "test_id": tally_form_id,
        "database_test_id": database_test_id,
        "form_url": form_url,
        "question_count": len(
            validated_test.questions
        )
    }
    
    
@mcp.tool()
def evaluate_submission(
    tally_form_id: str,
    tally_submission_id: str
) -> dict:

    # ---------------------------------------------
    # 1. Fetch submission from Tally
    # ---------------------------------------------

    submission = get_submission(
        tally_form_id,
        tally_submission_id
    )

    # ---------------------------------------------
    # 2. Load test from PostgreSQL
    # ---------------------------------------------

    test, question_mapping = (
        get_test_by_tally_form_id(
            tally_form_id
        )
    )

    # ---------------------------------------------
    # 3. Parse student answers
    # ---------------------------------------------

    answers = parse_submission(
        submission,
        question_mapping
    )

    # ---------------------------------------------
    # 4. Evaluate
    # ---------------------------------------------

    evaluation_result = evaluate_test(
        test,
        answers
    )

    # ---------------------------------------------
    # 5. Save submission
    # ---------------------------------------------

    submission_db_id = save_submission(
        tally_form_id=tally_form_id,
        tally_submission_id=tally_submission_id,
        submitted_at=submission[
            "submission"
        ].get("submittedAt")
    )

    # ---------------------------------------------
    # 6. Save result
    # ---------------------------------------------

    result_db_id = save_result(
        tally_submission_id=tally_submission_id,
        evaluation_result=evaluation_result
    )

    # ---------------------------------------------
    # 7. Return result
    # ---------------------------------------------

    return {
        "success": True,
        "tally_form_id": tally_form_id,
        "tally_submission_id": tally_submission_id,
        "submission_db_id": submission_db_id,
        "result_db_id": result_db_id,
        "evaluation": evaluation_result
    }
    

@mcp.tool()
def get_test_result(
    tally_submission_id: str
) -> dict:

    result = get_result_by_submission_id(
        tally_submission_id
    )

    return {
        "success": True,
        "tally_submission_id": tally_submission_id,
        "result": result
    }


if __name__ == "__main__":
    mcp.run()