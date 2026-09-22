import json
import os
import sys
import uuid

import httpx
from dotenv import load_dotenv

from schemas import Question, Test
from tally_webhook_setup import connect_tally_webhook

load_dotenv()

TALLY_API_KEY = os.getenv("TALLY_API_KEY")
TALLY_API_BASE_URL = "https://api.tally.so"
TALLY_API_VERSION = "2025-02-01"


def get_headers() -> dict[str, str]:
    if not TALLY_API_KEY:
        raise RuntimeError(
            "TALLY_API_KEY was not found in .env"
        )

    return {
        "Authorization": f"Bearer {TALLY_API_KEY}",
        "Content-Type": "application/json",
        "tally-version": TALLY_API_VERSION,
    }


def new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------
# TALLY BLOCK CREATION
# ---------------------------------------------------------

def create_form_title_block(title: str) -> dict:
    return {
        "type": "FORM_TITLE",
        "groupType": "TEXT",
        "payload": {
            "safeHTMLSchema": [
                [title]
            ],
            "title": title
        },
        "uuid": new_uuid(),
        "groupUuid": new_uuid()
    }


def create_description_block(description: str) -> dict:
    return {
        "type": "TEXT",
        "groupType": "TEXT",
        "payload": {
            "safeHTMLSchema": [
                [description]
            ]
        },
        "uuid": new_uuid(),
        "groupUuid": new_uuid()
    }


def create_question_title_block(
    question: str,
    question_group_uuid: str
) -> dict:
    return {
        "type": "TITLE",
        "groupType": "QUESTION",
        "payload": {
            "safeHTMLSchema": [
                [question]
            ]
        },
        "uuid": new_uuid(),
        "groupUuid": question_group_uuid
    }


def create_mcq_option(
    text: str,
    index: int,
    total_options: int,
    multiple_choice_group_uuid: str
) -> dict:
    return {
        "type": "MULTIPLE_CHOICE_OPTION",
        "groupType": "MULTIPLE_CHOICE",
        "payload": {
            "index": index,
            "isFirst": index == 0,
            "isLast": index == total_options - 1,
            "isRequired": True,
            "randomize": False,
            "isOtherOption": False,
            "allowMultiple": False,
            "hasMaxChoices": False,
            "colorCodeOptions": False,
            "hasBadge": True,
            "badgeType": "LETTERS",
            "hasDefaultAnswer": False,
            "text": text
        },
        "uuid": new_uuid(),
        "groupUuid": multiple_choice_group_uuid
    }


# ---------------------------------------------------------
# QUESTION → TALLY BLOCKS
# ---------------------------------------------------------

def create_mcq_blocks(
    question: Question
) -> tuple[list[dict], str]:

    question_group_uuid = new_uuid()
    multiple_choice_group_uuid = new_uuid()

    blocks = []

    blocks.append(
        create_question_title_block(
            question=question.question,
            question_group_uuid=question_group_uuid
        )
    )

    options = list(question.options.items())
    total_options = len(options)

    for index, (letter, option_text) in enumerate(options):

        option = f"{letter}. {option_text}"

        blocks.append(
            create_mcq_option(
                text=option,
                index=index,
                total_options=total_options,
                multiple_choice_group_uuid=multiple_choice_group_uuid
            )
        )

    return blocks, multiple_choice_group_uuid


# ---------------------------------------------------------
# TEST → COMPLETE TALLY FORM
# ---------------------------------------------------------

def create_test_blocks(
    test: Test
) -> tuple[list[dict], dict[int, str]]:

    blocks = []

    question_mapping = {}

    blocks.append(
        create_form_title_block(
            test.title
        )
    )

    if test.description:
        blocks.append(
            create_description_block(
                test.description
            )
        )

    for question in test.questions:

        if question.type != "MCQ":
            raise ValueError(
                f"Unsupported question type: {question.type}"
            )

        question_blocks, group_uuid = create_mcq_blocks(
            question
        )

        blocks.extend(question_blocks)

        # -----------------------------------------
        # Store our Question ID → Tally field UUID
        # -----------------------------------------

        question_mapping[question.id] = group_uuid

    return blocks, question_mapping

# ---------------------------------------------------------
# CREATE TALLY FORM
# ---------------------------------------------------------

def create_test_form(test: Test) -> dict:
    blocks, _question_mapping = create_test_blocks(test)

    payload = {
        "status": "PUBLISHED",
        "blocks": blocks,
    }

    response = httpx.post(
        f"{TALLY_API_BASE_URL}/forms",
        headers=get_headers(),
        json=payload,
        timeout=30.0
    )

    response.raise_for_status()

    result = response.json()

    # ---------------------------------------------------------
    # Automatically connect Tally webhook
    # ---------------------------------------------------------

    form_id = result["id"]

    print(
        f"Connecting webhook for Tally form {form_id}...",
        file=sys.stderr
    )

    webhook_result = connect_tally_webhook(form_id)

    if not webhook_result.get("success"):
        raise RuntimeError(
            f"Failed to connect Tally webhook: {webhook_result}"
        )

    print(
        f"Webhook connected for Tally form {form_id}.",
        file=sys.stderr
    )

    result["question_mapping"] = _question_mapping

    result["webhook"] = webhook_result

    return result


def get_form_submissions(form_id: str) -> dict:
    """
    Retrieve submissions for a Tally form.
    """

    url = f"{TALLY_API_BASE_URL}/forms/{form_id}/submissions"

    response = httpx.get(
        url,
        headers=get_headers(),
        timeout=30.0
    )

    if response.status_code == 401:
        raise RuntimeError(
            "Authentication failed. Check TALLY_API_KEY."
        )

    if response.status_code == 403:
        raise RuntimeError(
            "Tally API permission denied."
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"Tally form '{form_id}' was not found."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Tally API rate limit exceeded."
        )

    if not response.is_success:
        raise RuntimeError(
            f"Tally API request failed.\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

    return response.json()

def get_submission(
    form_id: str,
    submission_id: str
) -> dict:
    """
    Retrieve one specific Tally submission.
    """

    url = (
        f"{TALLY_API_BASE_URL}/forms/"
        f"{form_id}/submissions/{submission_id}"
    )

    response = httpx.get(
        url,
        headers=get_headers(),
        timeout=30.0
    )

    if response.status_code == 401:
        raise RuntimeError(
            "Authentication failed. Check TALLY_API_KEY."
        )

    if response.status_code == 403:
        raise RuntimeError(
            "Tally API permission denied."
        )

    if response.status_code == 404:
        raise RuntimeError(
            "Form or submission was not found."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Tally API rate limit exceeded."
        )

    if not response.is_success:
        raise RuntimeError(
            f"Tally API request failed.\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

    return response.json()

def get_form(form_id: str) -> dict:
    """
    Retrieve the complete Tally form.
    """

    url = f"{TALLY_API_BASE_URL}/forms/{form_id}"

    response = httpx.get(
        url,
        headers=get_headers(),
        timeout=30.0
    )

    if response.status_code == 401:
        raise RuntimeError(
            "Authentication failed. Check TALLY_API_KEY."
        )

    if response.status_code == 403:
        raise RuntimeError(
            "Tally API permission denied."
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"Tally form '{form_id}' was not found."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Tally API rate limit exceeded."
        )

    if not response.is_success:
        raise RuntimeError(
            f"Tally API request failed.\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

    return response.json()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_data = {
        "title": "GATE CSE - Paging Test",
        "description": (
            "Practice test on Operating Systems - Paging."
        ),
        "questions": [
            {
                "id": 1,
                "subject": "OS",
                "topic": "Paging",
                "type": "MCQ",
                "question": (
                    "Consider a system with 32-bit logical "
                    "addresses and a 4 KB page size. "
                    "How many bits are required for "
                    "the page offset?"
                ),
                "options": {
                    "A": "10 bits",
                    "B": "12 bits",
                    "C": "20 bits",
                    "D": "32 bits"
                },
                "correct_answer": "B",
                "explanation": (
                    "4 KB = 2^12 bytes, so 12 bits "
                    "are required for the page offset."
                ),
                "marks": 1,
                "negative_marks": 0.33,
                "source_url": None
            },
            {
                "id": 2,
                "subject": "OS",
                "topic": "Paging",
                "type": "MCQ",
                "question": (
                    "Which data structure is used to map "
                    "logical pages to physical frames?"
                ),
                "options": {
                    "A": "Page table",
                    "B": "Stack",
                    "C": "Queue",
                    "D": "Heap"
                },
                "correct_answer": "A",
                "explanation": (
                    "A page table maps logical pages "
                    "to physical memory frames."
                ),
                "marks": 1,
                "negative_marks": 0.33,
                "source_url": None
            }
        ]
    }

    try:

        print("=" * 70)
        print("CREATING GATE TEST")
        print("=" * 70)

        # Validate input using Pydantic
        test = Test(**test_data)

        print()
        print(f"Title     : {test.title}")
        print(f"Questions : {len(test.questions)}")

        # Create Tally form
        result = create_test_form(test)

        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

        print("=" * 70)

    except Exception as e:  # noqa: BLE001

        print()
        print("=" * 70)
        print("TALLY FORM CREATION FAILED")
        print("=" * 70)

        print(str(e))

        print("=" * 70)