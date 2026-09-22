import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TALLY_WEBHOOK_URL = os.getenv("TALLY_WEBHOOK_URL")
TALLY_WEBHOOK_SECRET = os.getenv("TALLY_WEBHOOK_SECRET")

from pathlib import Path

PLAYWRIGHT_PROFILE = str(
    Path(__file__).resolve().parents[1]
    / "pyq_pipeline"
    / "playwright_tally_profile"
)


def connect_tally_webhook(form_id: str) -> dict:
    if not TALLY_WEBHOOK_URL:
        raise RuntimeError(
            "TALLY_WEBHOOK_URL is not configured in .env"
        )

    if not TALLY_WEBHOOK_SECRET:
        raise RuntimeError(
            "TALLY_WEBHOOK_SECRET is not configured in .env"
        )

    form_url = f"https://tally.so/forms/{form_id}/integrations"

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            PLAYWRIGHT_PROFILE,
            headless=False,
        )

        try:
            page = (
                context.pages[0]
                if context.pages
                else context.new_page()
            )

            page.goto(form_url)
            page.wait_for_load_state("networkidle")

            # Find Webhooks integration.
            webhooks = page.get_by_text(
                "Webhooks",
                exact=True
            ).first

            if webhooks.count() == 0:
                raise RuntimeError(
                    "Could not find Webhooks integration."
                )

            webhooks_card = webhooks.locator("xpath=../..")

            connect_button = webhooks_card.get_by_role(
                "button",
                name="Connect"
            )

            if connect_button.count() != 1:
                raise RuntimeError(
                    "Could not uniquely locate Webhooks Connect button."
                )

            # Open connection dialog.
            connect_button.click()
            page.wait_for_timeout(700)

            # Endpoint URL.
            endpoint_input = page.locator(
                'input[placeholder="https://..."]'
            )

            if endpoint_input.count() != 1:
                raise RuntimeError(
                    "Could not find webhook endpoint input."
                )

            endpoint_input.fill(TALLY_WEBHOOK_URL)

            # Signing secret.
            add_secret_button = page.get_by_role(
                "button",
                name="Add a signing secret"
            )

            if add_secret_button.count() != 1:
                raise RuntimeError(
                    "Could not find signing secret button."
                )

            add_secret_button.click()
            page.wait_for_timeout(300)

            secret_input = page.locator(
                'input[placeholder="Enter a signing secret"]'
            )

            if secret_input.count() != 1:
                raise RuntimeError(
                    "Could not find signing secret input."
                )

            secret_input.fill(TALLY_WEBHOOK_SECRET)

            # Connect.
            dialog_connect = page.get_by_role(
                "button",
                name="Connect"
            ).last

            dialog_connect.click()

            page.wait_for_timeout(1500)

            # Verify.
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(700)

            body_text = page.locator("body").inner_text()

            if TALLY_WEBHOOK_URL not in body_text:
                raise RuntimeError(
                    "Webhook connection could not be verified."
                )

            return {
                "success": True,
                "form_id": form_id,
                "webhook_url": TALLY_WEBHOOK_URL,
            }

        finally:
            context.close()