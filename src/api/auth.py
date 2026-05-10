from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database.mongodb import users_collection
from .security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()

class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: UserSignup):
    existing_user = users_collection.find_one({
        "email": user.email
    })
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    hashed_pw = hash_password(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "role": "user"
    }
    users_collection.insert_one(new_user)
    return {"message": "User created successfully"}
    
@router.post("/login")
def login(user: UserLogin):
    existing_user = users_collection.find_one({
        "email": user.email
    })
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    valid_password = verify_password(
        user.password,
        existing_user["password"]
    )
    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    token = create_access_token({
        "user_id": str(existing_user["_id"]),
        "email": existing_user["email"],
        "role": existing_user["role"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": existing_user["role"],
        "username": existing_user["username"]
    }