from fastapi import FastAPI, Query, Path
from enum import Enum
import pandas as pd 
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Annotated, Literal

app = FastAPI(description=" learning from the Docs")

@app.get('/')
async def root():
    return {'message' : 'Hello World'}

@app.get("/items/{item_id}")
async def read_items(item_id:int):
    return {'item_id' : item_id}

class ModelName(str, Enum):
    alxnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get('/model/{model_name}')
def get_model(model_name : ModelName):
    if model_name is ModelName.alxnet:
        return {"model_name" : model_name, "model_id" : "A001"}
    if model_name.value == "lenet":
        return {"model_name" : model_name, "model_id" : "L001"}
    return {"model_name" : model_name, "model_id" : "R001"}

@app.get('/files/{file_path:path}')
async def read_csv(file_path : Path):
    df = pd.read_csv(file_path)
    return {"Data": df.head(1).to_dict(orient="records")}

class Item(BaseModel):
    name: str
    description: str
    price : float = 100.0
    tax : float | None = None

@app.post('/items/')
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({'price_with_tax' : price_with_tax})
    return item

@app.get('/item/')
async def read_items(q:Annotated[str | None , Query(max_length=50)] = None):
    return {'q' : q}

class FilterParams(BaseModel):
    limit : int = Field(100, gt=0, le=100)
    offset : int = Field(0, ge=0)
    order_by : Literal["Created_At", "Updated_at"] = "Created_At"
    tags : list[str] = []

@app.get('/items/')
async def read_items(filter_query : Annotated[FilterParams, Query()]):
    return filter_query

