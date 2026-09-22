import json

import httpx

from tally_service import TALLY_API_BASE_URL, get_headers

FORM_ID = "kdLMYo"


def test_get_form():
    url = f"{TALLY_API_BASE_URL}/forms/{FORM_ID}"

    response = httpx.get(
        url,
        headers=get_headers(),
        timeout=30.0,
    )

    print("STATUS:", response.status_code)
    print("BODY:")

    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:  # noqa: BLE001
        print(response.text)


if __name__ == "__main__":
    test_get_form()