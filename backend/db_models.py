from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.enums import (
    AgeInterval,
    EducationLevel,
    HugoStyleFamiliarity,
    ParagraphCategory,
    QuestionCategory,
    Choice,
    Author
)


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Enum(AgeInterval), nullable=False)
    education = Column(Enum(EducationLevel), nullable=False)
    studied_french_literature = Column(Boolean, nullable=False)
    hugo_style_familiarity = Column(Enum(HugoStyleFamiliarity), nullable=False)

class Paragraph(Base):
    __tablename__ = "paragraphs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file = Column(String, nullable=False)
    text = Column(String, nullable=False)
    category = Column(Enum(ParagraphCategory), nullable=False)
    author = Column(Enum(Author), nullable=False)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum(QuestionCategory), nullable=False)
    left_paragraph_id = Column(Integer, ForeignKey("paragraphs.id"))
    right_paragraph_id = Column(Integer, ForeignKey("paragraphs.id"))

    left_paragraph = relationship("Paragraph", foreign_keys=[left_paragraph_id])
    right_paragraph = relationship("Paragraph", foreign_keys=[right_paragraph_id])

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    participant_id = Column(Integer, ForeignKey("participants.id"))
    choice = Column(Enum(Choice), nullable=False)
