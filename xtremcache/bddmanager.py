import datetime
import logging
import os
from functools import lru_cache
from typing import Any, List, Type

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        create_engine)
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.orm.exc import NoResultFound

from xtremcache.exceptions import *
from xtremcache.utils import *


class BddManager():
    """Manage database to valid operations on cached files."""

    def __init__(self, data_base_dir: str, verbosity: int = logging.WARNING) -> None:
        self.__data_base_dir = os.path.realpath(data_base_dir)
        self.__verbosity = verbosity

    @property
    @lru_cache
    def __db_location(self) -> str:
        """Path to used database."""

        return os.path.join(self.__data_base_dir, f'{get_app_name()}.db')

    @property
    def size(self) -> int:
        """Current size of the database in bytes."""

        return os.path.getsize(self.__db_location)

    @property
    @lru_cache
    def __sqlite_db_location(self) -> str:
        """str to give to sqlalchemy to bridge the sqlite db."""

        return f'sqlite:///{self.__db_location}'

    @property
    @lru_cache
    def __engine(self) -> object:
        """Generate a sqlalchemy engine to manage the sqlite db."""

        dir = os.path.dirname(self.__db_location)
        os.makedirs(dir, exist_ok=True)
        engine = create_engine(
            self.__sqlite_db_location,
            echo=self.__verbosity<logging.INFO)
        return engine

    @property
    @lru_cache
    def Item(self) -> Type:
        """Abstract factory of Item (archive) in database.

        All element of database have to inhert the result of declarative_base(),
        that we don't what to expose globally."""

        self.__base = declarative_base()

        class Item(self.__base):
            """Item (archive) in database."""

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

            def copy_from(self, item: 'Item'):
                """Copy data members from another Item object."""

                for m in self.data_members_name:
                    setattr(self, m, getattr(item, m, None))

            def __eq__(self, other: 'Item'):
                """Compare only data members between two Items (not can_modifie and can_read)."""

                for m in self.data_members_name:
                    if getattr(self, m, None) != getattr(other, m, None):
                        return False
                return True

            @property
            def can_modifie(self) -> bool:
                """Return True if the Item can be modified safely."""

                return self.can_read and self.readers == 0

            @property
            def can_read(self) -> bool:
                """Return True if the Item can be read safely."""

                return not self.writer

            def __repr__(self) -> str:
                return f"<Item(id='{self.id}')>"

        self.__base.metadata.create_all(self.__engine)
        return Item

    def create_item(
            self,
            id: str,
            size: int = 0,
            readers: int = 0,
            writer: bool = False,
            archive_path: str = ''):
        """Factoty of database Item."""

        return self.Item(
            id=id,
            size=size,
            readers=readers,
            writer=writer,
            archive_path=archive_path)

    def get(self, id: str, create: bool = False):
        """Get a db Item by id.

        With create, create it if it's doesn't already exist."""

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
                    raise XtremCacheItemNotFoundError(e)
        return item

    def update(self, item) -> None:
        """Update a db Item by copy of a the given Item."""

        item_from_bdd = self.get(item.id)
        with Session(self.__engine) as session:
            try:
                item_from_bdd = session.query(self.Item).filter(self.Item.id.in_([item.id])).one()
                item_from_bdd.copy_from(item)
                session.commit()
            except Exception as e:
                raise XtremCacheItemNotFoundError(e)

    def delete(self, id: str):
        """Delete a db Item based on its id."""

        with Session(self.__engine) as session:
            try:
                session.query(self.Item).filter(self.Item.id.in_([id])).delete()
                session.commit()
                logging.info(f'"{id}" have been remove from cache db.')
            except Exception as e:
                raise XtremCacheRemoveError(e)

    def delete_all(self):
        """Delete all db Items."""

        with Session(self.__engine) as session:
            try:
                session.query(self.Item).delete()
                session.commit()
            except Exception as e:
                session.rollback()
                raise XtremCacheRemoveError(e)

    def get_all_values(self, member: str) -> List[Any]:
        """Return a list of the values of all Items member."""

        with Session(self.__engine) as session:
            try:
                values = session.query(member).all()
            except Exception as e:
                raise XtremCacheItemNotFoundError(e)
        return list(map(lambda v: v[0], values))

    @property
    def older(self):
        """Return the older db Item."""

        with Session(self.__engine) as session:
            try:
                item = session.query(self.Item).order_by(self.Item.created_date.desc()).first()
            except Exception as e:
                raise XtremCacheItemNotFoundError(e)
        return item
