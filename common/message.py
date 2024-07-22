from pydantic import BaseModel
from typing import Literal


class Data(BaseModel):
    id: str
    pic: str
    title: str
    path: str
    keyword: str
    location: str


class DatasetRequest(BaseModel):
    type: Literal['add', 'update', 'delete']
    data: list[Data]


class WebRequest(BaseModel):
    query: str


class WeatherRequest(BaseModel):
    city: str
    phone: str


class Response(BaseModel):
    code: str
    result: str
