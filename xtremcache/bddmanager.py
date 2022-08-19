from ast import Delete
import os
import datetime
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import Column
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base, load_only
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from xtremcache.utils import *
from xtremcache.exceptions import *

class BddManager():
    """Database to valid operations on cached files."""

    def __init__(
        self,
        data_base_dir):
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
    def Item(self):
        self.__base = declarative_base()
        class Item(self.__base):

            __tablename__ = 'items'
            data_members_name = [
                'id',
                'size',
                'readers',
                'writer',
                'archive_path'
            ]

            id = Column(String, primary_key=True, unique=True)
            size = Column(Integer, nullable=False)
            readers = Column(Integer, nullable=False)
            writer = Column(Boolean, nullable=False)
            archive_path = Column(String, nullable=False)
            created_date = Column(DateTime, default=datetime.datetime.utcnow)

            def copy_from(
                self,
                item):
                for m in self.data_members_name:
                    setattr(self, m, getattr(item, m, None))

            def __eq__(
                self,
                other):
                for m in self.data_members_name:
                    if getattr(self, m, None) != getattr(other, m, None):
                        return False
                return True

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
        return self.Item(
            id=id,
            size=size,
            readers=readers,
            writer=writer,
            archive_path=archive_path)

    def get(
        self,
        id,
        create=False):
        item = None
        with Session(self.__engine) as session:
            try:
                item = session.query(self.Item).filter(self.Item.id.in_([id])).one()
            except NoResultFound as e:
                if create:
                    session.add(self.create_item(
                        id=id,
                        writer=True))
                    session.commit()
                    return self.get(id)
                else:
                    raise XtremCacheItemNotFound(e)
        return item

    def update(
        self,
        item):
        item_from_bdd = self.get(item.id)
        with Session(self.__engine) as session:
            try:
                item_from_bdd = session.query(self.Item).filter(self.Item.id.in_([item.id])).one()
                item_from_bdd.copy_from(item)
                session.commit()
            except Exception as e:
                raise XtremCacheItemNotFound(e)
        
    def delete(
        self,
        id):
        with Session(self.__engine) as session:
            try:
                session.query(self.Item).filter(self.Item.id.in_([id])).delete()
                session.commit()
            except Exception as e:
                raise XtremCacheRemoveError(e)

    def delete_all(self):
        with Session(self.__engine) as session:
            try:
                session.query(self.Item).delete()
                session.commit()
            except Exception as e:
                session.rollback()
                raise XtremCacheRemoveError(e)

    def get_all_values(
        self,
        key):
        with Session(self.__engine) as session:
            try:
                values = session.query(key).all()
            except Exception as e:
                raise XtremCacheItemNotFound(e)
        return list(map(lambda v: v[0], values))

    def get_older(self):
        with Session(self.__engine) as session:
            try:
                item = session.query(self.Item).order_by(self.Item.created_date.desc()).first()
            except Exception as e:
                raise XtremCacheItemNotFound(e)
        return item