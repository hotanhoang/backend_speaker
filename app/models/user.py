from pydantic import BaseModel, Field
from typing import Optional
# from fastapi import UploadFile

class UserSchema(BaseModel):
    fullname: str = Field(...)
    number_phone: str = Field(...)
    password: str = Field(...)
    # feature: list = Field(...)

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "fullname": "Trần Nhật Trường",
    #             "number_phone" : "0961012528",
    #             "password" : "123123",
    #         }
    #     }
    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "fullname": "Trần Nhật Trường",
    #             "number_phone" : "0961012528",
    #             "feature" : []
    #         }
    #     }

class UserLogin(BaseModel):
    number_phone: str = Field(...)
    password: str = Field(...)

class UpdateFeature(BaseModel):
    number_phone: str = Field(...)
    
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }

def ResponseModelNodata(code , message):
    return {
        "data": {
            "sub" : ""
        },
        "code": code,
        "message": message,
    }

def ErrorResponseModel(code, message):
    return {"code": code, "message": message}