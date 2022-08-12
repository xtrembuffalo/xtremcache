import os
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine

from xtremcache.utils import Utils

class BddManager():
    """Data base to valid operations on cached files."""

    def __init__(self, data_base_dir):
        self.__data_base_dir = data_base_dir
        self.__base = declarative_base()
        self.__init_model_classes()
        self.__base.metadata.drop_all(self.__engine)
        self.__base.metadata.create_all(self.__engine)
        self.__session = Session(bind=self.__engine)

    def __del__(self):
        self.__engine.close()

    @property
    @lru_cache
    def __Item(self):
        class Item(self.__base):
            __tablename__ = 'items'

            id = Column(String, primary_key=True)
            size = Column(Integer, nullable=False, unique=True)

            def __repr__(self):
                return f"<Item(id='{self.id}')>"

        return Item
    
    def __init_model_classes(self):
        self.__Item

    def create_item(self, id:str, size:int):
        return self.__Item(id=id, size=size)

    @property
    @lru_cache
    def __engine(self):
        os.makedirs(self.__data_base_dir, exist_ok=True)
        cwd = os.getcwd()
        os.chdir(self.__data_base_dir)
        rt = create_engine(f"sqlite:///{Utils.get_app_name()}.db", echo=True)
        os.chdir(cwd)
        return rt

    def add_item(self, model):
        rt = False
        with Session(self.__engine) as session:
            session.add(model)
            rt = True
        return rt
