import os
import random

from pydantic import BaseModel, Field
from typing import ClassVar

from __root__ import DATA_PATH
from backend.enums import (
    AgeInterval,
    Author,
    Choice,
    EducationLevel,
    HugoStyleFamiliarity,
    ParagraphCategory,
    QuestionCategory,
)


class AutoIncrementModel(BaseModel):
    _counter: ClassVar[int] = 0  # Shared counter for all subclasses unless overridden

    id: int = Field(default_factory=lambda: AutoIncrementModel._get_next_id())

    @classmethod
    def _get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter


class Participant(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    age: AgeInterval
    education: EducationLevel
    studied_french_literature: bool
    hugo_style_familiarity: HugoStyleFamiliarity


class Paragraph(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    text: str
    category: ParagraphCategory
    author: Author

    @property
    def is_hugo(self) -> bool:
        return self.author == Author.hugo

    @classmethod
    def from_category(cls, category: ParagraphCategory) -> 'Paragraph':
        directory = str(os.path.join(DATA_PATH, category.value))
        file = random.choice(os.listdir(directory))

        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if category in [ParagraphCategory.hugo, ParagraphCategory.other]:
            author = Author[file.split('_')[0]]
        else:
            author = Author.genai

        return cls(text=text, category=category, author=author)


class Question(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    category: QuestionCategory
    left: Paragraph
    right: Paragraph


class Answer(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    question: Question
    participant: Participant
    choice: Choice
