from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
import model
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import oauth
from oauth import get_current_user

app = FastAPI(debug=True)


model.Base.metadata.create_all(bind=engine)
app.include_router(oauth.router) 

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


db_dependency = Annotated[Session, Depends(get_db)]	
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/", status_code=status.HTTP_200_OK)
async def verify_status(user:user_dependency, db: db_dependency):
	if user is None:
		raise HTTPException(status_code=401, detail='Authentication Failed')
	return {"User": user}


