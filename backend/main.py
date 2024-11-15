from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, Boolean, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.enums import (
    AgeInterval, EducationLevel, HugoStyleFamiliarity, Choice
)
from backend.questionnaire import Questionnaire

app = FastAPI()
app.mount("/frontend/static", StaticFiles(directory="static"), name="static")
Base = declarative_base()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DBParticipant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(SQLAlchemyEnum(AgeInterval), nullable=False)
    education = Column(SQLAlchemyEnum(EducationLevel), nullable=False)
    studied_french_literature = Column(Boolean, nullable=False)
    hugo_style_familiarity = Column(SQLAlchemyEnum(HugoStyleFamiliarity), nullable=False)


class DBAnswer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    question_id = Column(Integer, nullable=False)
    choice = Column(SQLAlchemyEnum(Choice), nullable=False)


Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/welcome.html") as f:
        return f.read()


@app.post("/participant/")
def create_participant(
    age: AgeInterval,
    education: EducationLevel,
    studied_french_literature: bool,
    hugo_style_familiarity: HugoStyleFamiliarity,
    db: SessionLocal = Depends(get_db),
):
    participant = DBParticipant(
        age=age,
        education=education,
        studied_french_literature=studied_french_literature,
        hugo_style_familiarity=hugo_style_familiarity,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@app.get("/start/")
def start_quiz(participant_id: int, db: SessionLocal = Depends(get_db)):
    participant = db.query(DBParticipant).filter(DBParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    questionnaire = Questionnaire()
    questions = [{"id": i.id, "left": i.left.text, "right": i.right.text} for i in questionnaire]
    return {"questions": questions}


@app.post("/answer/")
def save_answer(
    participant_id: int, question_id: int, choice: Choice, db: SessionLocal = Depends(get_db)
):
    participant = db.query(DBParticipant).filter(DBParticipant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    answer = DBAnswer(participant_id=participant_id, question_id=question_id, choice=choice)
    db.add(answer)
    db.commit()
    return {"message": "Answer saved successfully"}
