from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Users(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(300),unique=True)
	hashed_password = Column(String)


