from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime

class CreateUserModelSchema(BaseModel):
    username : str
    email : EmailStr
    password : str
    confirm_password :str
    role : str

    @model_validator(mode='before')
    def check_passwords(value):
        if value["password"] != value["confirm_password"]:
            raise ValueError("Passwords do not match")
        return value
    
class LoginUserModel(BaseModel):
    username : str
    password : str
    
class UserModelResponse(BaseModel):
    id : int
    username : str
    email : str

class CreateNotesModelSchema(BaseModel):
    title : str
    content : str
    user_id : int

class NotesModelResponse(BaseModel):
    id : int
    title : str
    content : str
    user_id : int
    created_at : datetime
