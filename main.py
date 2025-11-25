from fastapi import FastAPI, Depends, HTTPException
from app.db.database import SessionLocal,engine,Base
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserUpdate,UserResponse,UserCreate
from app.db.models import User
from app.auth.jwt_bearer import JWTBearer
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.db.models import User
from app.auth.jwt_handler import create_token
from sqlalchemy.orm import Session
from app.utils.hash import hash_password
from app.utils.hash import verify_password
from app.auth.jwt_handler import create_token

#create fastapi instance
app=FastAPI()

#bind database
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#root 
@app.get("/")
async def root():
    return {"Status": "OK"}

#login (authentication)
@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        raise HTTPException(404, "User not found")

    if not verify_password(credentials.password, user.password):
        raise HTTPException(401, "Invalid password")

    token = create_token({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })


#create user
@app.post("/users", response_model=UserResponse, dependencies=[Depends(JWTBearer(roles=["admin"]))])
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # Check duplicate username
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check duplicate email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pw,
        role=user.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


#get user by id
@app.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


#update user
@app.put("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
def update_user(user_id: int, updated: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    if updated.username is not None:
        user.username = updated.username

    if updated.email is not None:
        user.email = updated.email

    if updated.password is not None:
        user.password = updated.password

    if updated.role is not None:
        user.role = updated.role

    if updated.is_active is not None:
        user.is_active = updated.is_active

    db.commit()
    db.refresh(user)

    return user


#delete user
@app.delete("/users/{user_id}", dependencies=[Depends(JWTBearer(roles=["admin"]))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

