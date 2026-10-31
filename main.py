from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

app = FastAPI(title='Tennis-Database-API')

class ChoiceBase(BaseModel):
    choice_test: str
    is_correct: bool
class QuestionBase(BaseModel):
    question_text:str
    choices: List[ChoiceBase]

