from fastapi import FastAPI,HTTPException,Depends, status,Request
from pydantic import BaseModel
from typing import List, Optional
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from typing_extensions import Annotated
import auth
from auth import get_current_user
import random
import string

app=FastAPI()

app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

class ChoiceBase(BaseModel):
    choice_text:str
    is_correct:bool


class QuestionBase(BaseModel):
    question_text:str
    choices:List[ChoiceBase]

@app.middleware("http")
async def reuest_id_logging(request:Request,call_next):
    response=await call_next(request)
    random_letters=''.join(random.choice(string.ascii_letters) for _ in range(10))
    print(f"Log {random_letters}")
    response.headers["X-Request-ID"]=random_letters
    return response


@app.get("/",status_code=status.HTTP_200_OK)
async def user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authenticate failed')
    return {"User":user}



# to get all questions
@app.get("/questions")
async def read_questions(db:db_dependency):
    result= db.query(models.Questions).all()
    if not result:
        raise HTTPException(status_code=404, detail="Questions not found")
    return result


#get questions and choices
@app.get("/questions/{question_id}")
async def read_questions(questions_id:int,db:db_dependency):
    result= db.query(models.Questions).filter(models.Questions.id == questions_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id:int, db:db_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found for this question")
    return result


# Create and delete questions and choices
@app.post("/questions/")
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()
    return {"message": "Question created successfully", "question_id": db_question.id}

# Delete questions and their choices
@app.delete("/questions/{question_id}")
async def delete_questions(question_id:int, db:db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    db.delete(result)
    db.commit()
    return {"message": "Question and its choices deleted successfully"}

#update questions and choices
from fastapi import Body

@app.put("/questions/{question_id}")
async def update_question(
    question_id: int, 
    updated_question: QuestionBase = Body(...), 
    db: Session = Depends(get_db)
):
    # Find the question
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update question text
    db_question.question_text = updated_question.question_text

    # Remove old choices
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()

    # Add updated choices
    for choice in updated_question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=question_id
        )
        db.add(db_choice)

    db.commit()
    db.refresh(db_question)

    return {"message": "Question updated successfully", "question_id": db_question.id}
