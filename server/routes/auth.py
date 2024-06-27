import uuid
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Header
from database import get_db
from models.users import User
from pydantic_schemas.user_create import UserCreate
from pydantic_schemas.user_login import UserLogin
from sqlalchemy.orm import Session
from middleware.auth_middleware import auth_middlware
import jwt

router = APIRouter()

@router.post('/signup', status_code=201)
def sign_up(user: UserCreate,db=  Depends(get_db)):
    # check if user already exist
    user_db= db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(400, "User already exist!")
    # add the user in the database if not present
    hashed_pw= bcrypt.hashpw(user.password.encode(),bcrypt.gensalt())
    user_db=User(id=str(uuid.uuid4()), email=user.email, name=user.email, password=hashed_pw)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db;

@router.post('/login')
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # check if a user with same email already exist
    user_db = db.query(User).filter(User.email == user.email).first()

    if not user_db:
        raise HTTPException(400, 'User with this email does not exist!')
    
    # password matching or not
    is_match = bcrypt.checkpw(user.password.encode(), user_db.password)
    
    if not is_match:
        raise HTTPException(400, 'Incorrect password!')
    

    token = jwt.encode({'id': user_db.id}, 'password_key')
    
    return {'token': token, 'user': user_db}

@router.get('/')
def current_user_data(db: Session = Depends(get_db), user_dict= Depends(auth_middlware)):
    user= db.query(User).filter(User.id== user_dict['uid']).first();

    if not user:
        raise HTTPException(400,"User not found!")
    
    return user;
