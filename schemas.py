from typing import Literal

from pydantic import BaseModel, Field


class Question(BaseModel):
    id: int
    subject: str
    topic: str
    type: Literal["MCQ"]

    question: str

    options: dict[str, str] = Field(
        min_length=2,
        max_length=6
    )

    correct_answer: str

    explanation: str

    marks: float = 1.0
    negative_marks: float = 0.0

    source_url: str | None = None


class Test(BaseModel):
    title: str
    description: str

    questions: list[Question] = Field(
        min_length=1
    )