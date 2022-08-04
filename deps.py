from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jose import jwt
from pydantic import ValidationError
from schemas import TokenPayload, SystemUser
from models import User

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine, autoflush=False)

async def get_current_user(token: str = Depends(reuseable_oauth)) -> SystemUser:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    session = Session()
    user: Union[User, None] = session.query(User).filter_by(email=token_data.sub).first()
    session.close()
    
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return SystemUser(**user.__dict__)
