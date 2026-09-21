from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Question(BaseModel):

    id: int = Field(gt=0)

    subject: str = Field(min_length=1)

    topic: str = Field(min_length=1)

    type: Literal["MCQ"]

    question: str = Field(min_length=1)

    options: dict[str, str] = Field(
        min_length=2,
        max_length=6
    )

    correct_answer: str

    explanation: str = Field(min_length=1)

    marks: float = Field(gt=0)

    negative_marks: float = Field(ge=0)

    source_url: str | None = None

    # --------------------------------------------------
    # Validate option letters
    # --------------------------------------------------

    @field_validator("options")
    @classmethod
    def validate_options(cls, options):

        allowed_letters = {"A", "B", "C", "D", "E", "F"}

        for letter in options:

            if letter not in allowed_letters:
                raise ValueError(
                    f"Invalid option '{letter}'. "
                    f"Allowed options: A-F"
                )

        return options

    # --------------------------------------------------
    # Validate correct answer
    # --------------------------------------------------

    @model_validator(mode="after")
    def validate_correct_answer(self):

        if self.correct_answer not in self.options:

            raise ValueError(
                f"correct_answer '{self.correct_answer}' "
                f"does not exist in options "
                f"{list(self.options.keys())}"
            )

        return self


class Test(BaseModel):

    title: str = Field(min_length=1)

    description: str = Field(min_length=1)

    questions: list[Question] = Field(
        min_length=1
    )

    # --------------------------------------------------
    # Validate question IDs
    # --------------------------------------------------

    @model_validator(mode="after")
    def validate_question_ids(self):

        ids = [question.id for question in self.questions]

        if len(ids) != len(set(ids)):

            raise ValueError(
                "Question IDs must be unique."
            )

        return self