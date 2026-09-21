import json
from pathlib import Path

from fastmcp import Client

SERVER_PATH = Path(__file__).parent / "main.py"


async def main():

    async with Client(
        str(SERVER_PATH)
    ) as client:

        print("=" * 70)
        print("GATE TEST CREATOR MCP CLIENT")
        print("=" * 70)

        print("\nConnected to MCP server.")

        # --------------------------------------------------
        # Show available tools
        # --------------------------------------------------

        tools = await client.list_tools()

        print("\nAvailable tools:")

        for tool in tools:
            print(f"  • {tool.name}")

        # --------------------------------------------------
        # Interactive menu
        # --------------------------------------------------

        while True:

            print("\n" + "=" * 70)
            print("MENU")
            print("=" * 70)

            print("1. Create Test")
            print("2. Evaluate Submission")
            print("3. Get Test Result")
            print("4. Exit")

            choice = input(
                "\nEnter choice: "
            ).strip()

            # --------------------------------------------------
            # Create Test
            # --------------------------------------------------

            if choice == "1":

                test = {
                    "title": "GATE CSE - MCP Test",
                    "description": (
                        "Test created through the MCP server."
                    ),
                    "questions": [
                        {
                            "id": 1,
                            "subject": "Operating Systems",
                            "topic": "Memory Management",
                            "type": "MCQ",
                            "question": (
                                "What is the size of the page "
                                "offset for a 4 KB page?"
                            ),
                            "options": {
                                "A": "10 bits",
                                "B": "12 bits",
                                "C": "16 bits",
                                "D": "20 bits"
                            },
                            "correct_answer": "B",
                            "explanation": (
                                "4 KB = 2^12 bytes, so the "
                                "page offset requires 12 bits."
                            ),
                            "marks": 1,
                            "negative_marks": 0.33
                        },
                        {
                            "id": 2,
                            "subject": "Operating Systems",
                            "topic": "Memory Management",
                            "type": "MCQ",
                            "question": (
                                "Which data structure maps logical "
                                "pages to physical frames?"
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
                            "negative_marks": 0.33
                        }
                    ]
                }

                print("\nCreating test...")

                result = await client.call_tool(
                    "create_test",
                    {
                        "test": test
                    }
                )

                print("\nResult:")

                print(
                    json.dumps(
                        result.data,
                        indent=2
                    )
                )

            # --------------------------------------------------
            # Evaluate Submission
            # --------------------------------------------------

            elif choice == "2":

                form_id = input(
                    "\nEnter Tally Form ID: "
                ).strip()

                submission_id = input(
                    "Enter Tally Submission ID: "
                ).strip()

                print(
                    "\nEvaluating submission..."
                )

                result = await client.call_tool(
                    "evaluate_submission",
                    {
                        "tally_form_id": form_id,
                        "tally_submission_id": submission_id
                    }
                )

                print("\nEvaluation Result:")

                print(
                    json.dumps(
                        result.data,
                        indent=2
                    )
                )

            # --------------------------------------------------
            # Get Test Result
            # --------------------------------------------------

            elif choice == "3":

                submission_id = input(
                    "\nEnter Tally Submission ID: "
                ).strip()

                print(
                    "\nRetrieving stored result..."
                )

                result = await client.call_tool(
                    "get_test_result",
                    {
                        "tally_submission_id": submission_id
                    }
                )

                print("\nStored Result:")

                print(
                    json.dumps(
                        result.data,
                        indent=2
                    )
                )

            # --------------------------------------------------
            # Exit
            # --------------------------------------------------

            elif choice == "4":

                print("\nExiting...")
                break

            else:

                print(
                    "\nInvalid choice. "
                    "Please select 1-4."
                )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())