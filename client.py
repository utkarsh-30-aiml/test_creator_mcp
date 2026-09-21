import asyncio

from fastmcp import Client


async def main():

    client = Client("main.py")

    print("=" * 70)
    print("GATE TEST CREATOR MCP CLIENT")
    print("=" * 70)

    async with client:

        # ---------------------------------------------
        # Check connection
        # ---------------------------------------------

        print("\nConnected to MCP server.")

        # ---------------------------------------------
        # List available tools
        # ---------------------------------------------

        tools = await client.list_tools()

        print("\nAvailable tools:")

        for tool in tools:
            print(f"  • {tool.name}")

        # ---------------------------------------------
        # Test create_test tool
        # ---------------------------------------------

        test = {
            "title": "GATE CSE - MCP Test",
            "description": "Test created through the MCP server.",
            "questions": [
                {
                    "id": 1,
                    "subject": "OS",
                    "topic": "Paging",
                    "type": "MCQ",
                    "question": (
                        "What is the size of the page offset "
                        "for a 4 KB page?"
                    ),
                    "options": {
                        "A": "10 bits",
                        "B": "12 bits",
                        "C": "16 bits",
                        "D": "20 bits"
                    },
                    "correct_answer": "B",
                    "explanation": (
                        "4 KB = 2^12 bytes, so the page offset "
                        "requires 12 bits."
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
                    "negative_marks": 0.33,
                    "source_url": None
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
        print(result)

        print("\n" + "=" * 70)
        print("TEST COMPLETED")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())