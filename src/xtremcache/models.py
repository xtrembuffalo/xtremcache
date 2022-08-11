from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'

    id = Column(String, primary_key=True)

    def __repr__(self):
        return f"<Item(path='{self.path}')>"