from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from auth_routes import auth_router
from order_routes import order_router
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from schemas import Settings

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(auth_router)
app.include_router(order_router)
# models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text:str
    is_correct:bool

class QuestionBase(BaseModel):
    question_text:str
    choices:List[ChoiceBase]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/questions/")
async def read_allquestion( db : db_dependency):
    result = db.query(models.Questions).all()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result

@app.get("/questions/{question_id}")
async def read_question(question_id: int, db : db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result

from sqlalchemy.orm import Session

from fastapi import HTTPException

@app.delete("/questions/{question_id}")
async def delete_question_and_its_choices(question_id: int, db: db_dependency):
    try:
        # 1. Delete associated choices first to respect foreign key constraint
        choices_to_delete_respect_toQID = (
            db.query(models.Choices)
            .filter(models.Choices.question_id == question_id)
            .delete(synchronize_session="fetch")  # Important for SQLAlchemy ORM
        )

        # 2. Delete the question itself
        question = (
            db.query(models.Questions)
            .filter(models.Questions.id == question_id)
            .first()
        )
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        db.delete(question)
        db.commit()  # Commit changes to the database

        return {"message": "Question and its choices deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting question: {e}")



@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db : db_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found")
    return result

@app.get("/choices/")
async def read_Allchoices( db : db_dependency):
    result = db.query(models.Choices).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found")
    return result

@app.post("/questions/")
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct,question_id=db_question.id)
        db.add(db_choice)
    db.commit()


