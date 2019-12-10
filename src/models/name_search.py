
"""
ORM Model for table of object names to be used in word-search service
"""

import typing
from enum import Enum, auto
from sqlalchemy import Column, String, Integer, Enum as SQALEnum
from sqlalchemy.ext.declarative import declarative_base

base: typing.Any = declarative_base()


class EBodyType(Enum):
    """ Enum possible types of body for name_search """
    ASTEROID = auto()
    COMET = auto()


class NameSearch(base):
    """ ORM Class for small-bodies name search"""

    __tablename__ = 'name_search'
    search_text = Column(String, primary_key=True)
    target_text = Column(String)
    body_type = Column(String)

    def __init__(self, search_text: str, target_text: str, body_type: EBodyType) -> None:
        self.search_text = search_text
        self.target_text = target_text
        self.body_type = body_type.name

    def __repr__(self) -> str:
        return "NameSearch()"

    def __str__(self) -> str:
        return "<Class NameSearch: "+str(self.search_text)+" "+str(self.target_text)+">"
