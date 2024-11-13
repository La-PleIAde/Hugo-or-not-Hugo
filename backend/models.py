import os
import random

from pydantic import BaseModel, Field
from typing import ClassVar, Set

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

    file: str
    text: str
    category: ParagraphCategory
    author: Author

    @property
    def is_hugo(self) -> bool:
        return self.author == Author.hugo

    @classmethod
    def from_category(cls, category: ParagraphCategory, used_files: Set[str] = None) -> 'Paragraph':
        if not category in ParagraphCategory.__members__.values():
            raise ValueError(f'Invalid paragraph category "{category}"')

        directory = str(os.path.join(DATA_PATH, category.value))

        # Filter out files that are already used if used_files is provided
        files = [f for f in os.listdir(directory) if f not in (used_files or set())]

        if not files:
            raise ValueError(f"No available paragraphs in category {category} that haven't been used.")

        file = random.choice(files)

        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if category in [ParagraphCategory.hugo, ParagraphCategory.other]:
            author = Author[file.split('_')[0]]
        else:
            author = Author.genai

        # Add selected file to used_files to avoid re-selection
        if used_files is not None:
            used_files.add(file)

        return cls(file=file, text=text, category=category, author=author)


class Question(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    category: QuestionCategory
    left: Paragraph
    right: Paragraph

    @classmethod
    def from_category(cls, category: QuestionCategory, used_files: Set[str] = None) -> 'Question':
        if not category in QuestionCategory.__members__.values():
            raise ValueError(f'Invalid question category "{category}"')

        paragraph_mapping = {
            QuestionCategory.A: ParagraphCategory.other,
            QuestionCategory.B: ParagraphCategory.neutralized,
            QuestionCategory.C: ParagraphCategory.other2hugo,
            QuestionCategory.D: ParagraphCategory.restored,
        }

        if category == QuestionCategory.E:
            p_category = random.choice(list(ParagraphCategory))
            p1 = Paragraph.from_category(p_category)
            p2 = Paragraph.from_category(p_category)
        else:
            p1 = Paragraph.from_category(ParagraphCategory.hugo, used_files=used_files)
            p2 = Paragraph.from_category(paragraph_mapping.get(category))

        left, right = random.sample([p1, p2], k=2)

        return cls(category=category, left=left, right=right)


class Answer(AutoIncrementModel):
    _counter: ClassVar[int] = 0

    question: Question
    participant: Participant
    choice: Choice
