# GATE Test Creator MCP Server

An MCP (Model Context Protocol) server for creating and evaluating **GATE-style MCQ tests** using **FastMCP, Tally Forms, and PostgreSQL**.

The server allows an LLM application or MCP client to:

1. Create a GATE MCQ test.
2. Automatically create a corresponding Tally form.
3. Publish the test through a Tally form URL.
4. Retrieve student submissions from Tally.
5. Parse submitted answers.
6. Automatically evaluate answers.
7. Calculate positive and negative marks.
8. Store tests, submissions, and results in PostgreSQL.
9. Retrieve previously stored evaluation results.

---

# 1. Project Overview

## Problem

Creating an online GATE test manually requires several separate operations:

```text
Create questions
      ↓
Create online form
      ↓
Publish form
      ↓
Collect student responses
      ↓
Evaluate answers
      ↓
Calculate score
      ↓
Store result
```

This project automates that entire workflow.

The MCP server exposes the functionality as tools that can be called by an MCP-compatible client or an LLM application.

---

# 2. Architecture

The overall architecture is:

```text
                    ┌─────────────────────────┐
                    │       LLM Application   │
                    │                         │
                    │ Chatbot / Agent / App   │
                    └────────────┬────────────┘
                                 │
                                 │ MCP
                                 ▼
                    ┌─────────────────────────┐
                    │      FastMCP Server      │
                    │        main.py           │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │ Tally API   │    │ PostgreSQL  │    │ Evaluation  │
       │             │    │             │    │ Pipeline    │
       └──────┬──────┘    └─────────────┘    └──────┬──────┘
              │                                     │
              ▼                                     ▼
       Tally Form                              Parser
              │                                     │
              ▼                                     ▼
       Student Submission                     Evaluator
```

---

# 3. Complete Workflow

The application follows this lifecycle:

```text
CREATE
   ↓
PUBLISHED
   ↓
SUBMITTED
   ↓
EVALUATED
```

Detailed flow:

```text
LLM/Application
      │
      │ create_test()
      ▼
FastMCP Server
      │
      ├── Validate test using Pydantic
      │
      ├── Create Tally form
      │
      ├── Create MCQ blocks
      │
      ├── Generate question mapping
      │
      └── Save test in PostgreSQL
      │
      ▼
Tally Form URL
      │
      │ Student opens form
      ▼
Student submits answers
      │
      ▼
Tally Submission
      │
      │ evaluate_submission()
      ▼
Retrieve submission
      │
      ▼
submission_parser.py
      │
      ▼
Convert Tally IDs → Application Question IDs
      │
      ▼
evaluator.py
      │
      ├── Correct answer
      ├── Incorrect answer
      └── Unanswered
      │
      ▼
Calculate score
      │
      ▼
PostgreSQL
      │
      ├── Save submission
      └── Save result
      │
      ▼
get_test_result()
      │
      ▼
Stored result returned
```

---

# 4. Folder Structure

Current project structure:

```text
test_creator_mcp/
│
├── main.py
├── client.py
│
├── tally_service.py
├── schemas.py
├── submission_parser.py
├── evaluator.py
├── database.py
│
├── init_db.py
│
├── test_repository.py
│
├── test_database.py
├── test_db_tables.py
├── test_repository.py
├── test_save_test.py
├── test_get_saved.py
├── test_get_test.py
│
├── test_submissions.py
├── test_single_submission.py
├── test_submission_parser.py
├── test_evaluator.py
├── test_save_submission.py
├── test_save_result.py
├── test_get_result.py
├── test_evaluation_flow.py
├── test_get_submissions.py
├── test_inspect_submission.py
│
├── .env
└── pyproject.toml
```

---

# 5. File Responsibilities

## `main.py`

Main MCP server.

Responsibilities:

* Create FastMCP server.
* Define MCP tools.
* Validate incoming test data.
* Call Tally service.
* Call database repository.
* Parse submissions.
* Evaluate tests.
* Return results to MCP clients.

Currently exposes:

```text
create_test
evaluate_submission
get_test_result
```

---

# 6. `client.py`

Local MCP client used for testing the server.

It:

1. Starts/connects to `main.py`.
2. Lists available MCP tools.
3. Displays an interactive menu.
4. Calls MCP tools.
5. Displays returned results.

Current menu:

```text
1. Create Test
2. Evaluate Submission
3. Get Test Result
4. Exit
```

Run:

```powershell
uv run python client.py
```

---

# 7. `schemas.py`

Contains Pydantic models for validating test data.

Main models:

```text
Question
Test
```

## Question

```python
class Question(BaseModel):
    id: int
    subject: str
    topic: str
    type: Literal["MCQ"]
    question: str
    options: dict[str, str]
    correct_answer: str
    explanation: str
    marks: float
    negative_marks: float
    source_url: str | None
```

### Validation

Question ID must be positive:

```text
id > 0
```

Subject must not be empty.

Topic must not be empty.

Question type must be:

```text
MCQ
```

Question text must not be empty.

Options must contain between 2 and 6 options.

Allowed option letters:

```text
A
B
C
D
E
F
```

Correct answer must exist in the options.

For example:

```json
{
  "options": {
    "A": "Stack",
    "B": "Queue",
    "C": "Heap",
    "D": "Tree"
  },
  "correct_answer": "A"
}
```

is valid.

But:

```json
{
  "options": {
    "A": "Stack",
    "B": "Queue"
  },
  "correct_answer": "C"
}
```

is invalid.

---

# 8. Test Schema

A test contains:

```text
title
description
questions
```

Example:

```json
{
  "title": "GATE CSE Operating Systems Test",
  "description": "Operating Systems MCQ test",
  "questions": [
    {
      "id": 1,
      "subject": "Operating Systems",
      "topic": "Memory Management",
      "type": "MCQ",
      "question": "What is the size of the page offset for a 4 KB page?",
      "options": {
        "A": "10 bits",
        "B": "12 bits",
        "C": "16 bits",
        "D": "20 bits"
      },
      "correct_answer": "B",
      "explanation": "4 KB = 2^12 bytes, so the page offset requires 12 bits.",
      "marks": 1,
      "negative_marks": 0.33
    }
  ]
}
```

Question IDs must be unique within a test.

---

# 9. `tally_service.py`

Handles communication with the Tally API.

Main functions:

```text
get_headers()
new_uuid()

create_form_title_block()
create_description_block()

create_question_title_block()
create_mcq_option()
create_mcq_blocks()

create_test_blocks()
create_test_form()

get_form()
get_form_submissions()
get_submission()
```

---

# 10. Tally API Authentication

The Tally API key is loaded from `.env`.

Example:

```env
TALLY_API_KEY=your_tally_api_key
```

Requests use:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
tally-version: 2025-02-01
```

The application communicates with:

```text
https://api.tally.so
```

---

# 11. Tally Form Creation

When `create_test()` is called, the server converts the application test into Tally blocks.

For example:

```text
Question
   ↓
TITLE block
   +
MULTIPLE_CHOICE_OPTION blocks
```

For:

```text
What is the size of the page offset for a 4 KB page?
```

with:

```text
A. 10 bits
B. 12 bits
C. 16 bits
D. 20 bits
```

Tally receives a question block and four multiple-choice option blocks.

---

# 12. Question Mapping

One of the most important parts of this project is the mapping between:

```text
Application Question ID
        ↓
Tally blockGroupUuid
        ↓
Tally Question ID
```

The application maintains:

```python
{
    1: "9c2da304-8bac-4cf2-ac5a-6cd036c844b8",
    2: "0ec33157-8f2d-4860-9626-de836f402b81"
}
```

The important point is:

**The application's question ID and Tally's question ID are not the same thing.**

The parser therefore uses Tally's `blockGroupUuid` to correctly identify which application question a submitted answer belongs to.

---

# 13. `submission_parser.py`

Converts raw Tally submission data into a simple application format.

Input:

```text
Raw Tally submission
```

Output:

```python
{
    1: "B. 12 bits",
    2: "C. Queue"
}
```

The parser performs:

```text
Tally response.questionId
          ↓
Tally questions[]
          ↓
blockGroupUuid
          ↓
question_mapping
          ↓
Application question ID
```

It also handles unanswered questions.

Example:

```python
{
    1: "B. 12 bits",
    2: None
}
```

---

# 14. `evaluator.py`

Evaluates student answers.

Function:

```python
evaluate_test(
    test,
    answers
)
```

For every question:

```text
Correct
    → +marks

Incorrect
    → -negative_marks

Unanswered
    → 0
```

Example:

```text
Question marks       = 1
Negative marks       = 0.33
```

Correct:

```text
+1.00
```

Incorrect:

```text
-0.33
```

Unanswered:

```text
0.00
```

---

# 15. Evaluation Example

Suppose:

```text
Q1:
Correct answer = B
Student answer = B
Marks = 1

Q2:
Correct answer = A
Student answer = C
Negative marks = 0.33
```

Result:

```text
Q1 → Correct   → +1.00
Q2 → Incorrect → -0.33
```

Total:

```text
1.00 - 0.33 = 0.67
```

---

# 16. `database.py`

Provides PostgreSQL connection functionality.

The database URL is read from `.env`.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/test_creator
```

Connection is created using:

```python
psycopg2.connect(DATABASE_URL)
```

---

# 17. PostgreSQL Database

Database:

```text
test_creator
```

PostgreSQL version used during development:

```text
PostgreSQL 18.6
```

Windows service:

```text
postgresql-x64-18
```

---

# 18. Database Tables

The application currently uses four major tables:

```text
tests
questions
submissions
results
```

Relationship:

```text
tests
  │
  ├─────────────── questions
  │
  └─────────────── submissions
                       │
                       └──────── results
```

---

# 19. `tests` Table

```sql
CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    tally_form_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Stores:

```text
Internal test ID
Tally form ID
Test title
Description
Creation timestamp
```

---

# 20. `questions` Table

Stores questions belonging to a test.

Important fields:

```text
id
test_id
question_id
tally_question_id
question
options
correct_answer
explanation
marks
negative_marks
```

The table maintains the relationship between the application question and Tally question.

---

# 21. `submissions` Table

Stores student submissions.

Fields:

```text
id
test_id
tally_submission_id
submitted_at
created_at
```

`tally_submission_id` is unique.

Therefore the same Tally submission is not stored multiple times.

---

# 22. `results` Table

Stores evaluation results.

Fields:

```text
id
submission_id
total_score
correct
incorrect
unanswered
total_questions
result_json
created_at
```

The complete evaluation is also stored inside:

```text
result_json
```

as PostgreSQL JSONB.

---

# 23. `init_db.py`

Creates the required PostgreSQL tables.

Run:

```powershell
uv run python init_db.py
```

Expected:

```text
Database initialized successfully.
```

The script uses:

```sql
CREATE TABLE IF NOT EXISTS
```

so running it again does not recreate existing tables.

---

# 24. `test_repository.py`

Contains database repository functions.

Important functions include:

```text
save_test()
get_test_by_tally_form_id()

save_submission()
save_result()

get_result_by_submission_id()
```

---

# 25. `save_test()`

Stores:

```text
Test
+
Questions
+
Tally Form ID
+
Question Mapping
```

Returns the internal PostgreSQL test ID.

Example:

```text
Tally Form ID:
PdoJdB

Database Test ID:
7
```

---

# 26. `get_test_by_tally_form_id()`

Retrieves the stored test using:

```text
tally_form_id
```

Returns:

```python
(
    Test,
    question_mapping
)
```

This allows the evaluation pipeline to reconstruct the original test after the student submits the Tally form.

---

# 27. `save_submission()`

Stores a student's submission.

It first checks whether the submission already exists.

If it exists:

```text
Return existing submission ID
```

instead of inserting a duplicate.

This makes the operation effectively idempotent for the same Tally submission.

---

# 28. `save_result()`

Stores evaluation results.

It also checks whether a result already exists for the submission.

If the result already exists:

```text
Return existing result ID
```

Otherwise a new result is inserted.

---

# 29. `get_result_by_submission_id()`

Retrieves a stored result using:

```text
Tally Submission ID
```

Example:

```text
o9QO16V
```

Returns:

```json
{
  "result_id": 5,
  "submission_id": 6,
  "total_score": 0.67,
  "correct": 1,
  "incorrect": 1,
  "unanswered": 0,
  "total_questions": 2,
  "result": {},
  "created_at": "..."
}
```

---

# 30. MCP Server

The MCP server is implemented using FastMCP.

Server initialization:

```python
from fastmcp import FastMCP

mcp = FastMCP("GATE Test Creator")
```

Tools are registered using:

```python
@mcp.tool()
```

---

# 31. MCP Tool 1 — `create_test`

Creates a new GATE test.

Signature:

```python
create_test(test: dict) -> dict
```

## Input

```json
{
  "test": {
    "title": "GATE CSE Test",
    "description": "Operating Systems Test",
    "questions": [
      {
        "id": 1,
        "subject": "Operating Systems",
        "topic": "Memory Management",
        "type": "MCQ",
        "question": "What is the size of the page offset for a 4 KB page?",
        "options": {
          "A": "10 bits",
          "B": "12 bits",
          "C": "16 bits",
          "D": "20 bits"
        },
        "correct_answer": "B",
        "explanation": "4 KB = 2^12 bytes, so the page offset requires 12 bits.",
        "marks": 1,
        "negative_marks": 0.33
      }
    ]
  }
}
```

## Processing

```text
Input
 ↓
Pydantic validation
 ↓
Create Tally form
 ↓
Save test to PostgreSQL
 ↓
Return Tally form URL
```

## Output

```json
{
  "success": true,
  "test_id": "PdoJdB",
  "database_test_id": 7,
  "form_url": "https://tally.so/r/PdoJdB",
  "question_count": 2
}
```

---

# 32. MCP Tool 2 — `evaluate_submission`

Evaluates a Tally submission.

Signature:

```python
evaluate_submission(
    tally_form_id: str,
    tally_submission_id: str
) -> dict
```

## Input

```json
{
  "tally_form_id": "PdoJdB",
  "tally_submission_id": "o9QO16V"
}
```

## Processing

```text
Tally Form ID
       +
Submission ID
       ↓
Retrieve Tally submission
       ↓
Retrieve test from PostgreSQL
       ↓
Parse submission
       ↓
Evaluate answers
       ↓
Save submission
       ↓
Save result
       ↓
Return evaluation
```

## Output

```json
{
  "success": true,
  "tally_form_id": "PdoJdB",
  "tally_submission_id": "o9QO16V",
  "submission_db_id": 6,
  "result_db_id": 5,
  "evaluation": {
    "total_score": 0.67,
    "correct": 1,
    "incorrect": 1,
    "unanswered": 0,
    "total_questions": 2,
    "results": [
      {
        "question_id": 1,
        "student_answer": "B. 12 bits",
        "correct_answer": "B",
        "status": "correct",
        "marks": 1.0,
        "explanation": "4 KB = 2^12 bytes, so the page offset requires 12 bits."
      },
      {
        "question_id": 2,
        "student_answer": "C. Queue",
        "correct_answer": "A",
        "status": "incorrect",
        "marks": -0.33,
        "explanation": "A page table maps logical pages to physical memory frames."
      }
    ]
  }
}
```

---

# 33. MCP Tool 3 — `get_test_result`

Retrieves a previously stored result.

Signature:

```python
get_test_result(
    tally_submission_id: str
) -> dict
```

## Input

```json
{
  "tally_submission_id": "o9QO16V"
}
```

## Output

```json
{
  "success": true,
  "tally_submission_id": "o9QO16V",
  "result": {
    "result_id": 5,
    "submission_id": 6,
    "total_score": 0.67,
    "correct": 1,
    "incorrect": 1,
    "unanswered": 0,
    "total_questions": 2,
    "result": {
      "correct": 1,
      "incorrect": 1,
      "unanswered": 0,
      "total_score": 0.67,
      "total_questions": 2,
      "results": []
    },
    "created_at": "2026-09-21T22:07:03.193488"
  }
}
```

---

# 34. Error Handling

The application validates input before processing.

Examples of invalid data:

## Invalid correct answer

```json
{
  "options": {
    "A": "Stack",
    "B": "Queue"
  },
  "correct_answer": "C"
}
```

Produces a validation error because:

```text
C does not exist in options
```

---

## Duplicate question IDs

```json
{
  "questions": [
    {
      "id": 1
    },
    {
      "id": 1
    }
  ]
}
```

Produces:

```text
Question IDs must be unique.
```

---

## Unknown Tally form

If the form does not exist in PostgreSQL:

```text
Test with Tally form ID 'XXXX' was not found.
```

---

## Unknown submission

If a result is requested for a submission that does not exist:

```text
Result for Tally submission ID 'XXXX' was not found.
```

---

# 35. Environment Variables

Create:

```text
.env
```

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/test_creator

TALLY_API_KEY=YOUR_TALLY_API_KEY
```

Do not commit `.env` to GitHub.

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# 36. Installation

## Step 1 — Clone the project

```powershell
git clone <repository-url>
cd test_creator_mcp
```

---

# 37. Create Virtual Environment

Using `uv`:

```powershell
uv venv
```

Activate:

```powershell
.venv\Scripts\activate
```

---

# 38. Install Dependencies

```powershell
uv sync
```

or:

```powershell
uv pip install -r requirements.txt
```

depending on the project setup.

The project uses packages including:

```text
fastmcp
psycopg2-binary
python-dotenv
pydantic
httpx
```

---

# 39. PostgreSQL Setup

Make sure PostgreSQL is running.

Windows PowerShell:

```powershell
Get-Service *postgres*
```

Expected:

```text
Status   Name
------   ----
Running  postgresql-x64-18
```

Create database:

```text
test_creator
```

Example using PostgreSQL:

```sql
CREATE DATABASE test_creator;
```

Then configure:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/test_creator
```

---

# 40. Initialize Database

Run:

```powershell
uv run python init_db.py
```

Expected:

```text
Database initialized successfully.
```

Verify tables using PostgreSQL.

Expected tables:

```text
tests
questions
submissions
results
```

---

# 41. Test Database Connection

Run:

```powershell
uv run python test_database.py
```

Expected:

```text
Database connection successful.
```

---

# 42. Start/Test MCP Server

For local stdio usage, the MCP server can be started by an MCP client using:

```text
main.py
```

The included client does this automatically.

Run:

```powershell
uv run python client.py
```

Expected:

```text
======================================================================
GATE TEST CREATOR MCP CLIENT
======================================================================

Connected to MCP server.

Available tools:
  • create_test
  • evaluate_submission
  • get_test_result
```

---

# 43. Testing `create_test`

Run:

```powershell
uv run python client.py
```

Select:

```text
1
```

The client sends the test to the MCP server.

Expected response:

```json
{
  "success": true,
  "test_id": "...",
  "database_test_id": 7,
  "form_url": "https://tally.so/r/...",
  "question_count": 2
}
```

Open the returned:

```text
form_url
```

in a browser.

---

# 44. Student Submission

The student completes the Tally form.

For example:

```text
Q1 → B. 12 bits
Q2 → C. Queue
```

Tally generates a submission ID.

Example:

```text
o9QO16V
```

---

# 45. Evaluate Submission

Run the client:

```powershell
uv run python client.py
```

Select:

```text
2
```

Enter:

```text
Enter Tally Form ID: PdoJdB
Enter Tally Submission ID: o9QO16V
```

The server retrieves and evaluates the submission.

Expected:

```text
Correct     : 1
Incorrect   : 1
Unanswered  : 0
Total Score : 0.67
```

---

# 46. Retrieve Stored Result

Run:

```powershell
uv run python client.py
```

Select:

```text
3
```

Enter:

```text
o9QO16V
```

The application retrieves the stored PostgreSQL result.

This verifies that the result is persisted and can be retrieved independently of the original evaluation request.

---

# 47. Exposing the MCP Server to an LLM Application

There are two main ways to connect an LLM application.

## Option A — Local STDIO

Recommended during development.

Architecture:

```text
LLM Application
       │
       │ MCP Client
       ▼
    main.py
       │
       ├── Tally
       └── PostgreSQL
```

The LLM application launches:

```text
main.py
```

as an MCP server process.

This is useful when:

* MCP client and server are on the same machine.
* Developing locally.
* Testing tools.
* Building a desktop AI application.

The current `client.py` demonstrates this approach.

FastMCP 4 deprecates inferring stdio transport from a plain string path; using a `Path` object is preferred for local clients.

---

# 48. Option B — HTTP MCP Server

For a remote LLM application, the server can be exposed over HTTP using FastMCP's HTTP transport.

Conceptually:

```text
                 Internet / Network
                       │
                       ▼
              ┌─────────────────┐
              │ LLM Application │
              └────────┬────────┘
                       │
                       │ MCP over HTTP
                       ▼
              ┌─────────────────┐
              │ FastMCP Server  │
              │    main.py      │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Tally             PostgreSQL
```

A typical deployment exposes the MCP endpoint through an HTTP server.

For example, with the appropriate FastMCP HTTP transport configuration:

```text
http://localhost:8000/mcp
```

The exact transport/CLI options should match the FastMCP version installed in the environment. FastMCP 4 supports modern HTTP MCP connections and the FastMCP client can connect to a server URL directly.

---

# 49. Example HTTP MCP Client

A remote application can conceptually connect using:

```python
from fastmcp import Client

async with Client(
    "http://localhost:8000/mcp"
) as client:

    tools = await client.list_tools()

    result = await client.call_tool(
        "create_test",
        {
            "test": {
                "title": "GATE CSE Test",
                "description": "Operating Systems Test",
                "questions": []
            }
        }
    )
```

The important difference is:

### Local

```python
Client(Path("main.py"))
```

### Remote

```python
Client("http://localhost:8000/mcp")
```

The URL is treated as a remote MCP endpoint.

---

# 50. LLM Agent Architecture

The intended production architecture is:

```text
                         ┌──────────────────┐
                         │       User       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   LLM / Agent    │
                         │                  │
                         │ GPT / Llama /    │
                         │ Other MCP client │
                         └────────┬─────────┘
                                  │
                                  │ MCP
                                  ▼
                    ┌──────────────────────────┐
                    │    GATE Test Creator     │
                    │       MCP Server         │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
        Tally API           PostgreSQL          Evaluator
```

The LLM does not directly need to understand:

```text
Tally API
PostgreSQL
question mappings
submission parsing
score calculation
```

Instead, the LLM sees MCP tools.

---

# 51. Example LLM Interaction

A user could ask an AI application:

```text
Create a 10-question GATE CSE Operating Systems
test focusing on deadlocks and memory management.
Use 1 mark for correct answers and 0.33 negative
marking for incorrect answers.
```

The LLM can construct:

```json
{
  "title": "GATE CSE - Operating Systems",
  "description": "Deadlocks and Memory Management",
  "questions": [
    ...
  ]
}
```

Then call:

```text
create_test
```

The MCP server returns:

```json
{
  "success": true,
  "test_id": "ABC123",
  "database_test_id": 10,
  "form_url": "https://tally.so/r/ABC123",
  "question_count": 10
}
```

The LLM application can then present the form URL to the user.

---

# 52. Example Tool Call — `create_test`

An MCP client sends:

```json
{
  "test": {
    "title": "GATE CSE - Operating Systems",
    "description": "Deadlocks and Memory Management",
    "questions": [
      {
        "id": 1,
        "subject": "Operating Systems",
        "topic": "Deadlocks",
        "type": "MCQ",
        "question": "Which algorithm is used for deadlock avoidance?",
        "options": {
          "A": "Banker's Algorithm",
          "B": "Round Robin",
          "C": "FIFO",
          "D": "LRU"
        },
        "correct_answer": "A",
        "explanation": "Banker's Algorithm is used for deadlock avoidance.",
        "marks": 1,
        "negative_marks": 0.33
      }
    ]
  }
}
```

---

# 53. Example Tool Call — `evaluate_submission`

```json
{
  "tally_form_id": "ABC123",
  "tally_submission_id": "XYZ789"
}
```

Server processing:

```text
Retrieve submission
        ↓
Parse answers
        ↓
Load test
        ↓
Evaluate
        ↓
Save submission
        ↓
Save result
```

---

# 54. Example Tool Call — `get_test_result`

```json
{
  "tally_submission_id": "XYZ789"
}
```

Returns the stored result.

This allows an LLM application to retrieve a previous result without performing the evaluation again.

---

# 55. Data Flow Between Systems

## Test Creation

```text
LLM
 ↓
MCP
 ↓
Pydantic
 ↓
Tally API
 ↓
Tally Form
 ↓
PostgreSQL
```

## Submission Evaluation

```text
Tally Submission
 ↓
Tally API
 ↓
Parser
 ↓
Question Mapping
 ↓
Evaluator
 ↓
PostgreSQL
```

## Result Retrieval

```text
LLM
 ↓
MCP
 ↓
PostgreSQL
 ↓
Stored Result
```

---

# 56. Why PostgreSQL Is Used

Tally is responsible for:

```text
Form creation
Student UI
Submission collection
```

PostgreSQL is responsible for:

```text
Test persistence
Question persistence
Submission persistence
Evaluation persistence
Result retrieval
```

This separation allows Tally to remain the form/submission provider while PostgreSQL becomes the application's persistent database.

---

# 57. Why the Question Mapping Is Necessary

Tally generates its own IDs.

For example:

```text
Our question:

ID = 1
```

Tally might internally represent it using:

```text
Tally Question ID = ZRVag0
```

and:

```text
blockGroupUuid = 9c2da304-8bac-4cf2-ac5a-6cd036c844b8
```

Therefore:

```text
Application Question
       ↓
Tally Group UUID
       ↓
Tally Question
       ↓
Student Response
```

Without this mapping, it would be difficult to reliably determine which application question a student answered.

---

# 58. Current Verified Example

A complete real test was successfully created:

```text
Tally Form ID:
PdoJdB
```

Submission:

```text
o9QO16V
```

Student answers:

```text
Q1 → B. 12 bits
Q2 → C. Queue
```

Evaluation:

```text
Q1 → Correct
Q2 → Incorrect
```

Score:

```text
1.00 - 0.33 = 0.67
```

Database:

```text
submission_db_id = 6
result_db_id     = 5
```

Result retrieval through the MCP tool also succeeded.

---

# 59. Testing Strategy

The project follows incremental testing.

Recommended order:

```text
1. Database connection
        ↓
2. Database tables
        ↓
3. Tally API
        ↓
4. Tally form creation
        ↓
5. Question mapping
        ↓
6. Submission retrieval
        ↓
7. Submission parser
        ↓
8. Evaluator
        ↓
9. Repository
        ↓
10. MCP create_test
        ↓
11. MCP evaluate_submission
        ↓
12. MCP get_test_result
```

This makes debugging easier because each layer is verified independently.

---

# 60. Important Design Principles

## Separation of concerns

Each module has a specific responsibility:

```text
main.py
    MCP layer

schemas.py
    Validation layer

tally_service.py
    Tally API layer

submission_parser.py
    Tally → Application conversion

evaluator.py
    Evaluation logic

database.py
    Database connection

test_repository.py
    Database operations

client.py
    MCP client/testing interface
```

---

# 61. Idempotency

Duplicate submissions are handled.

For example:

```text
Submission ID:
o9QO16V
```

If `evaluate_submission()` is called again, the repository checks whether the submission already exists.

Likewise, the result is checked before insertion.

This prevents unnecessary duplicate database records.

---

# 62. Security Considerations

Never commit:

```text
.env
```

to Git.

Do not expose:

```text
TALLY_API_KEY
DATABASE_URL
PostgreSQL password
```

in source code.

For production deployment:

```text
LLM Application
      ↓
HTTPS
      ↓
MCP Server
      ↓
Tally/PostgreSQL
```

Use:

```text
HTTPS
authentication
authorization
environment secrets
database access controls
```

rather than exposing an unauthenticated development server.

---

# 63. `.gitignore`

Recommended:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.idea/
.vscode/
```

---

# 64. Future Improvements

The current MVP is working. Possible future improvements include:

## 1. Dynamic test creation

Instead of the current hardcoded `client.py` test, allow the user/LLM to provide:

```text
title
description
number of questions
subject
topic
difficulty
marks
negative marks
```

---

## 2. Automatic evaluation

Currently:

```text
Student submits
       ↓
Application calls evaluate_submission()
```

Future architecture:

```text
Student submits
       ↓
Tally webhook
       ↓
MCP/backend
       ↓
Automatic evaluation
       ↓
Database
```

This removes the need to manually provide the submission ID.

---

## 3. Difficulty levels

Add:

```text
easy
medium
hard
```

to questions.

---

## 4. Question generation

An LLM could generate:

```text
Subject
Topic
Question
Options
Correct answer
Explanation
```

and then call:

```text
create_test
```

---

## 5. Test status

Potential statuses:

```text
DRAFT
PUBLISHED
SUBMITTED
EVALUATED
```

---

## 6. Student analytics

Future results could include:

```text
Accuracy
Percentage
Topic-wise performance
Correct questions
Incorrect questions
Unanswered questions
Time taken
```

---

## 7. Result APIs

Additional MCP tools could be added:

```text
get_test
get_test_submissions
get_test_statistics
get_student_history
get_question_analysis
```

---

# 65. Current MCP API Summary

| Tool                  | Input                                  | Purpose                       |
| --------------------- | -------------------------------------- | ----------------------------- |
| `create_test`         | `test`                                 | Create Tally test and save it |
| `evaluate_submission` | `tally_form_id`, `tally_submission_id` | Evaluate and save submission  |
| `get_test_result`     | `tally_submission_id`                  | Retrieve stored result        |

---

# 66. Current Project Status

The following components have been verified:

```text
Pydantic validation             ✅
Tally API connection             ✅
Tally form creation              ✅
MCQ creation                     ✅
Question mapping                 ✅
Tally submission retrieval       ✅
Submission parsing               ✅
Answer evaluation                ✅
Negative marking                 ✅
PostgreSQL connection            ✅
Database initialization          ✅
Test persistence                 ✅
Submission persistence            ✅
Result persistence               ✅
Duplicate submission handling    ✅
Duplicate result handling        ✅
MCP create_test                  ✅
MCP evaluate_submission          ✅
MCP get_test_result              ✅
End-to-end workflow              ✅
```

---

# 67. Quick Start

For a fresh environment:

```powershell
cd D:\TY-sem-2\edai-7th-sem\test_creator_mcp
```

Create/activate environment:

```powershell
uv venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
uv sync
```

Configure:

```text
.env
```

with:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/test_creator
TALLY_API_KEY=YOUR_TALLY_API_KEY
```

Initialize:

```powershell
uv run python init_db.py
```

Test database:

```powershell
uv run python test_database.py
```

Start local MCP client:

```powershell
uv run python client.py
```

Then:

```text
1 → Create Test
2 → Evaluate Submission
3 → Get Test Result
4 → Exit
```

---

# 68. End-to-End Example

```text
User
 │
 │ "Create a GATE OS test"
 ▼
LLM
 │
 │ create_test()
 ▼
MCP Server
 │
 ├── Validate Test
 │
 ├── Create Tally Form
 │
 └── Save PostgreSQL data
 │
 ▼
https://tally.so/r/PdoJdB
 │
 │ Student submits
 ▼
Tally
 │
 ▼
Submission: o9QO16V
 │
 │ evaluate_submission()
 ▼
MCP Server
 │
 ├── Get submission
 ├── Parse answers
 ├── Load test
 ├── Evaluate
 ├── Save submission
 └── Save result
 │
 ▼
Score = 0.67
 │
 │ get_test_result()
 ▼
LLM Application
 │
 ▼
Display result to user
```

---

# 69. Final Architecture

The project can be summarized as:

```text
                    GATE TEST CREATOR
                           │
                           ▼
                  ┌──────────────────┐
                  │   LLM / Client   │
                  └────────┬─────────┘
                           │
                           │ MCP
                           ▼
                  ┌──────────────────┐
                  │    FastMCP       │
                  │     main.py      │
                  └────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     ┌─────────┐      ┌──────────┐    ┌───────────┐
     │  Tally  │      │PostgreSQL│    │ Evaluator │
     │   API   │      │          │    │           │
     └────┬────┘      └────┬─────┘    └─────┬─────┘
          │                │                │
          ▼                ▼                ▼
       Forms           Persistence       Scores
       Answers         Tests             Results
       Responses       Questions
                       Submissions
```

The MCP layer provides a clean interface between an LLM/application and the underlying GATE test infrastructure.

---

# 70. License

Add the project's chosen license here, for example:

```text
MIT License
```

if the project is intended to be open source.
