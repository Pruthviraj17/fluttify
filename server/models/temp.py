from sqlalchemy import TEXT, VARCHAR, Column, LargeBinary

from models.base import Base
from sqlalchemy.orm import relationship

class Temp(Base):
    __tablename__ = "temp"

    id = Column(TEXT, primary_key=True)
    name= Column(VARCHAR(100))
    email= Column(VARCHAR(100))
    password= Column(LargeBinary)