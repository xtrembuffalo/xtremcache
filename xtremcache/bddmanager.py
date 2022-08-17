from ast import Delete
import os
import re
import time
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import Column
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from xtremcache.utils import *

class BddManager():
    """Data base to valid operations on cached files."""

    def __init__(self, data_base_dir):
        self.__data_base_dir = os.path.realpath(data_base_dir)

    @property
    @lru_cache
    def __db_location(self):
        return os.path.join(self.__data_base_dir, f"{get_app_name()}.db")

    @property
    @lru_cache
    def __sqlite_db_location(self):
        return f"sqlite:///{self.__db_location}"
    
    @property
    @lru_cache
    def __engine(self):
        dir = os.path.dirname(self.__db_location)
        os.makedirs(dir, exist_ok=True)
        return create_engine(self.__sqlite_db_location, echo=True)

    @property
    @lru_cache
    def __Item(self):
        self.__base = declarative_base()
        class Item(self.__base):
            __tablename__ = 'items'

            id = Column(String, primary_key=True, unique=True)
            size = Column(Integer, nullable=False)
            readers = Column(Integer, nullable=False)
            writer = Column(Boolean, nullable=False)
            archive_path = Column(String, nullable=False)

            def copy_from(self, item):
                self.id = item.id
                self.size = item.size
                self.readers = item.readers
                self.writer = item.writer
                self.archive_path = item.archive_path

            @property
            def can_modifie(self):
                return self.can_read and self.readers == 0
            
            @property
            def can_read(self):
                return not self.writer

            def __repr__(self):
                return f"<Item(id='{self.id}')>"
        self.__base.metadata.create_all(self.__engine)
        return Item
    
    def create_item(
        self,
        id:str,
        size:int = 0,
        readers:int = 0,
        writer:bool = False,
        archive_path:str = ''
        ):
        return self.__Item(
            id=id,
            size=size,
            readers=readers,
            writer=writer,
            archive_path=archive_path)

    def get_item(self, id, create=False):
        item = None
        with Session(self.__engine) as session:
            try:
                item = session.query(self.__Item).filter(self.__Item.id.in_([id])).one()
            except NoResultFound as e:
                item = None if not create else self.create_item(id=id, writer=True)
                if item:
                    session.add(item)
                    session.commit()
                    return self.get_item(id)
        return item

    def update(self, item):
        valid = False
        with Session(self.__engine) as session:
            try:
                item_from_bdd = session.query(self.__Item).filter(self.__Item.id.in_([item.id])).one()
                item_from_bdd.copy_from(item)
                session.commit()
                valid = True
            except NoResultFound as e:
                print(e)
                valid = False
        return valid

    def delete(self, id):
        valid = False
        with Session(self.__engine) as session:
            try:
                session.query(self.__Item).filter(self.__Item.id.in_([id])).delete()
                session.commit()
                valid = True
            except NoResultFound as e:
                valid = False
            
        return valid

    def delete_all(self):
        valid = False
        with Session(self.__engine) as session:
            try:
                session.query(self.__Item).delete()
                session.commit()
                valid = True
            except:
                session.rollback()
        return valid

def create_bdd_manager(data_base_dir) -> BddManager:
    return BddManager(data_base_dir)