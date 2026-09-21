from fastmcp import FastMCP

from schemas import Test
from tally_service import create_test_form

mcp = FastMCP("GATE Test Creator")


@mcp.tool()
def create_test(test: dict) -> dict:
    """
    Create a GATE MCQ test using Tally.

    The input must contain:
    - title
    - description
    - questions

    Each question must contain:
    - id
    - subject
    - topic
    - type
    - question
    - options
    - correct_answer
    - explanation
    - marks
    - negative_marks
    - source_url
    """

    # -------------------------------------------------
    # 1. Validate incoming test JSON
    # -------------------------------------------------

    validated_test = Test(**test)

    # -------------------------------------------------
    # 2. Create Tally form
    # -------------------------------------------------

    result = create_test_form(validated_test)

    # -------------------------------------------------
    # 3. Extract useful information
    # -------------------------------------------------

    test_id = result["id"]

    form_url = f"https://tally.so/r/{test_id}"

    return {
        "success": True,
        "test_id": test_id,
        "form_url": form_url,
        "question_count": len(validated_test.questions)
    }


if __name__ == "__main__":
    mcp.run()