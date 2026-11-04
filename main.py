from rich.repr import Result
from openpyxl.chart import title
from fastapi import FastAPI, Query, Path, Body, Cookie, Request, Response, Header
from fastapi import File, UploadFile
from enum import Enum
import pandas as pd 
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Literal

from datetime import datetime, time, timedelta
from uuid import UUID

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
    model_config = {'extra' : 'forbid'}
    limit : int = Field(100, gt=0, le=100)
    offset : int = Field(0, ge=0)
    order_by : Literal["Created_At", "Updated_at"] = "Created_At"
    tags : list[str] = []
class Tags(BaseModel):
    Enter_tags : list[str] = set()

@app.get('/items/models/')
async def read_items(filter_query : Annotated[FilterParams, Query()]):
    return filter_query

@app.get('items/multiplr_models/')
async def two_methods(filters : Annotated[FilterParams | None, Query()],
    Tags : Annotated[Tags, Query()]):
    return [filters, Tags]

# Body Parameters

@app.put("/items/{item_id}")
async def update_item(item_id : Annotated[int, Path()],
    q:str | None = None,
    item: Item | None =None,):
    results = {"Item_id" : item_id}
    if q:
        results.update({"q" : q})
    if item:
        results.update({"item" : item.model_dump()})
    return results

class User(BaseModel):
    username : str
    full_name : str | None = None

@app.put("/items/{item_id}")
async def update_item_2(item_id : int, item: Item, user : User, importance : Annotated[int, Body(embed = True)]):
    results = {
        "item_id" : item_id,
        "Item" : item,
        "user" : user,
        "importance" : importance
    }
    return results

@app.put("/items/{item_id}")
async def update_item_3(item_id : int, item : Annotated[Item, Body(embed=True)]):
    result = {
        "item_id" : item_id,
        "item" : item}
    return result

@app.put("/items/{item_id}")
def update_item_4(item_id, int, item : Item):
    result = {"item_id" : item_id, "item" : item}
    return result

class Image(BaseModel):
    url : HttpUrl
    name : str

@app.put("/item/{item_id}")
async def update_item_5(item_id : int, url : HttpUrl):
    results = {"item_id" : item_id, "URL" : url}
    return results 

@ app.get("/Post/{post_id}")
async def get_post(post_id : UUID,
            post_date : Annotated[datetime, Body(examples=['2026-11-04 12:00:00'])],
            content : Annotated[list[str] | None , Body()] = None):
    result = {"post_id" : post_id,"post_date" : post_date, "content":content}
    return result

@app.get("/login")
def login(response: Response):
    response.set_cookie(
        key="username",
        value="Advait"
    )
    return {"message": "Login successful"}

@ app.get("/items_header/")
async def read_items(user_agent: Annotated[str | None, Header()]):
    return {
        "User-Agent" : user_agent
    }

@app.post("/upload_file/")
async def upload_file(files: Annotated[list[UploadFile], File()]):
    result = []
    for file in files:
        content = await file.read()
        with open(file.filename, 'wb') as f:
            f.write(content)
        result.append(file.filename)
    return {"filenames": result}


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Patch list[UploadFile] schemas so Swagger UI renders file pickers
    for schema in openapi_schema.get("components", {}).get("schemas", {}).values():
        for prop in schema.get("properties", {}).values():
            if prop.get("type") == "array" and "items" in prop:
                if prop["items"].get("contentMediaType") == "application/octet-stream":
                    prop["items"]["format"] = "binary"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi