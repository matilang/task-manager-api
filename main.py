from enum import Enum
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Annotated

class Model(BaseModel):
    name : str
    age  : int | None = 0
    country_of_origin : str | None = None


app = FastAPI()


@app.get('/models/')
async def try_query(number : int = 12, message : str | None = "my message", q : Annotated[str | None, 
                                                                                          Query(max_length=50,
                                                                                                alias='max-lenght',
                                                                                                title='Happy query',
                                                                                                description='Trying features for query',
                                                                                                deprecated=True)] = None):
    return {"number" : number, "message" : message, "q" : q}

@app.post('/models/')
async def createModel(model : Model):
    model_dict = model.dict()
    if model.age is not None:
        year_of_birth = 2025 - model.age
        model_dict.update({"year_of_birth" : year_of_birth})
    return model_dict