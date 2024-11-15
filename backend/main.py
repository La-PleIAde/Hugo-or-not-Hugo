from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import SessionLocal, engine
from backend.db_models import Base, Participant, Answer
from backend.schemas import ParticipantCreate, AnswerCreate
from backend.questionnaire import Questionnaire

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. Replace with specific origins in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/participants/")
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    db_participant = Participant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@app.post("/api/v1/questionnaire")
def get_questionnaire(data: dict, db: Session = Depends(get_db)):
    participant_id = data.get("participant_id")
    db_participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    questionnaire = Questionnaire()
    questions = []
    for question in questionnaire:
        questions.append({
            "category": question.category.value,
            "left": question.left.text,
            "right": question.right.text,
        })
    return {"questions": questions}


@app.post("/api/v1/answers/")
def submit_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    db_answer = Answer(**answer.dict())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return {"status": "success", "id": db_answer.id}

