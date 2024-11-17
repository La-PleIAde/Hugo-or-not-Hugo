import os
import random
from typing import ClassVar, Set, Dict, List

from pydantic import BaseModel, Field

from __root__ import DATA_PATH
from backend.enums import (
    Author,
    ParagraphCategory,
    QuestionCategory,
)


DEFAULT_QUESTIONS_DISTRIBUTION = {
    QuestionCategory.A: 4,
    QuestionCategory.B: 2,
    QuestionCategory.C: 4,
    QuestionCategory.D: 4,
    QuestionCategory.E: 0
}


class AutoIncrementModel(BaseModel):
    _counter: ClassVar[int] = 0  # Shared counter for all subclasses unless overridden

    id: int = Field(default_factory=lambda: AutoIncrementModel._get_next_id())

    @classmethod
    def _get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter


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
            text = f.read().strip().replace("[MASK]", "[MASQUE]")

        if category in [ParagraphCategory.hugo, ParagraphCategory.other]:
            author = Author[file.split('_')[0]]
        else:
            author = Author.genai

        # Add selected file to used_files to avoid re-selection
        if used_files is not None:
            used_files.add(file)

        return cls(file=file, text=text, category=category, author=author)

    @classmethod
    def from_category_with_postfix(cls, category: ParagraphCategory, source_id: int) -> 'Paragraph':
        """
        Finds a paragraph with the given source_id in the specified category.
        """
        if category not in ParagraphCategory.__members__.values():
            raise ValueError(f'Invalid paragraph category "{category}"')

        directory = str(os.path.join(DATA_PATH, category.value))
        postfix = f"_{source_id}"

        # Filter out files that do not match the source_id or are already used
        files = [f for f in os.listdir(directory) if f.endswith(postfix + '.txt')]

        if not files:
            raise ValueError(
                f"No available paragraphs in category {category} with postfix '{postfix}'.")

        file = random.choice(files)

        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            text = f.read().strip()

        author = Author.genai if category != ParagraphCategory.hugo else Author[file.split('_')[0]]

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
        elif category == QuestionCategory.D:
            source_paragraph = Paragraph.from_category(ParagraphCategory.hugo, used_files=used_files)
            source_id = int(source_paragraph.file.split('_')[-1].split('.')[0])
            restored_paragraph = Paragraph.from_category_with_postfix(ParagraphCategory.restored, source_id)
            p1, p2 = source_paragraph, restored_paragraph
        else:
            p1 = Paragraph.from_category(ParagraphCategory.hugo, used_files=used_files)
            p2 = Paragraph.from_category(paragraph_mapping.get(category))

        left, right = random.sample([p1, p2], k=2)

        return cls(category=category, left=left, right=right)


class Questionnaire:
    def __init__(self, n_questions_per_category: Dict[QuestionCategory, int] = None):
        if not n_questions_per_category:
            n_questions_per_category = DEFAULT_QUESTIONS_DISTRIBUTION
        self.questions = self._init_questions(n_questions_per_category)

    def _init_questions(self, n_questions_per_category):
        questions = []

        for category, n in n_questions_per_category.items():
            questions += self._get_questions_by_category(n, category)
        random.shuffle(questions)
        return questions

    @staticmethod
    def _get_questions_by_category(n: int, category: QuestionCategory) -> List[Question]:
        used_hugo_files = set()
        questions = []

        for i in range(n):
            questions.append(Question.from_category(category, used_hugo_files))
        return questions

    def __iter__(self):
        return iter(self.questions)
