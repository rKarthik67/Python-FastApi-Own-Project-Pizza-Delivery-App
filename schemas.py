from pydantic import BaseModel,Field
from typing import Optional


class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]


    class Config:
        orm_mode = True
        schema_extra={
            'example':{
                "username":"ashwin",
                "email":"ashwin67@gmail.com",
                "password":"password",
                "is_staff":False,
                "is_active":True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key:str='6d1b0406a8d60699f673ff11eaafbf31a83025ac00f7ffaf264700dd60c2a620'


class LoginModel(BaseModel):
    username:str
    password:str
    


class OrderModel(BaseModel):
    id : Optional[int]
    quantity:int
    order_status=str=Field(default="PENDING")
    pizza_size=str=Field(default="SMALL")
    user_id:Optional[int]
    

    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "quantity":2,
                "pizza_size":"LARGE"
            }
        }
