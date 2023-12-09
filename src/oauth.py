from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from model import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
	prefix='/oauth',
	tags=['oauth']
)

SECRET_KEY = '85f3f644b421c07c73b1cf84e66a7fe1'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token")

class CreateUserRequest(BaseModel):
	username: str
	password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
	username : str or None=None

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
	create_user_model = Users(
		username=create_user_request.username,
		hashed_password=bcrypt_context.hash(create_user_request.password),
	)
	db.add(create_user_model)
	db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = 'Could not validate the user.')
	token = create_access_token(user.username, user.id, timedelta(minutes=60))
	return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = 'Invalid username or password')
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = 'Invalid username or password')
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
	encode = {'sub':username, 'id':user_id}
	expires = datetime.utcnow() + expires_delta
	encode.update({'exp':expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if username is None or user_id is None:
        	raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
        						detail='Could not validate the user.')
        return {'username': username, 'id': user_id}
    except JWTError:
    	raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    						detail='Could not validate the user.')