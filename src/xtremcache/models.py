from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'

    id = Column(String, primary_key=True)

    def __repr__(self):
        return f"<Item(path='{self.path}')>"