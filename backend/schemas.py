from pydantic import BaseModel

from backend.enums import AgeInterval, EducationLevel, HugoStyleFamiliarity, Choice

class ParticipantCreate(BaseModel):
    age: AgeInterval
    education: EducationLevel
    studied_french_literature: bool
    hugo_style_familiarity: HugoStyleFamiliarity

class AnswerCreate(BaseModel):
    question_id: int
    participant_id: int
    choice: Choice
