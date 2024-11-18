import os

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import SessionLocal, engine, DB_PATH
from backend.db_models import Base, Participant, Answer, Question, Paragraph
from backend.models import Questionnaire
from backend.schemas import ParticipantCreate, AnswerCreate

app = FastAPI()

# Create all database tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. Replace with specific origins in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Admin authentication dependency
ADMIN_KEY = os.getenv("ADMIN_KEY", "root")

def admin_required(admin_key: str = Header(...)):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")

@app.post("/api/v1/participants/")
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    db_participant = Participant(**participant.model_dump())
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

    # Generate the questionnaire using the existing logic
    questionnaire = Questionnaire()  # Assumes this generates questions and associates paragraphs

    questions = []
    for question in questionnaire:
        # Save Paragraphs to DB if not already saved
        for paragraph in [question.left, question.right]:
            db_paragraph = db.query(Paragraph).filter_by(file=paragraph.file).first()
            if not db_paragraph:
                db_paragraph = Paragraph(
                    file=paragraph.file,
                    text=paragraph.text,
                    category=paragraph.category,
                    author=paragraph.author,
                )
                db.add(db_paragraph)
                db.commit()
                db.refresh(db_paragraph)
            paragraph.id = db_paragraph.id  # Ensure question object has correct IDs

        # Save Question to DB
        db_question = Question(
            category=question.category,
            left_paragraph_id=question.left.id,
            right_paragraph_id=question.right.id,
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        # Add to response
        questions.append({
            "id": db_question.id,
            "category": db_question.category.value,
            "left": question.left.text,
            "right": question.right.text,
        })

    return {"questions": questions}

@app.post("/api/v1/answers/")
def submit_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    db_answer = Answer(**answer.model_dump())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return {"status": "success", "id": db_answer.id}

@app.get("/api/v1/download-db", dependencies=[Depends(admin_required)])
def download_db():
    """
    Endpoint to download the database file. Only accessible to admins.
    """
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database file not found")
    return FileResponse(DB_PATH, media_type="application/octet-stream", filename="database.db")
