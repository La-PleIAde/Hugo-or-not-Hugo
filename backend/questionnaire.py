import random
from typing import Dict, List

from backend.enums import QuestionCategory
from backend.models import Question

DEFAULT_QUESTIONS_DISTRIBUTION = {
    QuestionCategory.A: 4,
    QuestionCategory.B: 2,
    QuestionCategory.C: 4,
    QuestionCategory.D: 4,
    QuestionCategory.E: 0
}


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
