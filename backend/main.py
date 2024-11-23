import os
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.database import SessionLocal, engine
from backend.db_models import Base, Participant, Answer, Question, Paragraph
from backend.schemas import ParticipantCreate, AnswerCreate

# Initialize FastAPI apps for participants and admins
participant_app = FastAPI()
admin_app = FastAPI()

# Create main FastAPI instance
app = FastAPI()

# Create all database tables
Base.metadata.create_all(bind=engine)

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


# ======================
# Participant Endpoints
# ======================
@participant_app.post("/participants/")
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    db_participant = Participant(**participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@participant_app.post("/questionnaire/")
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


@participant_app.post("/answers/")
def submit_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    db_answer = Answer(**answer.model_dump())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return {"status": "success", "id": db_answer.id}


# ==================
# Admin Endpoints
# ==================
@admin_app.get("/participants/", dependencies=[Depends(admin_required)])
def list_participants(
    db: Session = Depends(get_db),
    age: str = Query(None),
    education: str = Query(None)
):
    filters = []
    if age:
        filters.append(Participant.age == age)
    if education:
        filters.append(Participant.education == education)

    participants = db.query(Participant).filter(and_(*filters)).all()
    return participants


@admin_app.get("/paragraphs/", dependencies=[Depends(admin_required)])
def list_paragraphs(
    db: Session = Depends(get_db),
    category: str = Query(None),
    author: str = Query(None)
):
    filters = []
    if category:
        filters.append(Paragraph.category == category)
    if author:
        filters.append(Paragraph.author == author)

    paragraphs = db.query(Paragraph).filter(and_(*filters)).all()
    return paragraphs


@admin_app.get("/questions/", dependencies=[Depends(admin_required)])
def list_questions(
    db: Session = Depends(get_db),
    category: str = Query(None)
):
    filters = []
    if category:
        filters.append(Question.category == category)

    questions = db.query(Question).filter(and_(*filters)).all()
    return questions


@admin_app.get("/answers/", dependencies=[Depends(admin_required)])
def list_answers(
    db: Session = Depends(get_db),
    participant_id: int = Query(None),
    question_id: int = Query(None)
):
    filters = []
    if participant_id:
        filters.append(Answer.participant_id == participant_id)
    if question_id:
        filters.append(Answer.question_id == question_id)

    answers = db.query(Answer).filter(and_(*filters)).all()
    return answers


# Add domain-specific CORS settings
participant_origins = ["https://hugo-or-not-hugo.netlify.app"]
admin_origins = ["*"]

participant_app.add_middleware(
    CORSMiddleware,
    allow_origins=participant_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=admin_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount sub-applications
app.mount("/api/v1/participant", participant_app)
app.mount("/api/v1/admin", admin_app)
