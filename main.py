from fastmcp import FastMCP

from schemas import Test
from tally_service import create_test_form
from test_repository import save_test

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


if __name__ == "__main__":
    mcp.run()