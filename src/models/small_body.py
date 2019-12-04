
"""
ORM Model for table of object names to be used in word-search service
"""

import typing
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

base: typing.Any = declarative_base()


class SmallBody(base):
    """ ORM Small-Body Class"""

    __tablename__ = 'small_bodies'
    numid = Column(Integer, primary_key=True)
    unaccented = Column(String)
    accented = Column(String)

    def __init__(self, numid: int, unaccented: str, accented: str) -> None:
        self.numid = numid
        self.accented = accented
        self.unaccented = unaccented

    def __repr__(self) -> str:
        return "SmallBody()"

    def __str__(self) -> str:
        return "<Class SmallBody: "+str(self.accented)+" "+str(self.unaccented)+" "+str(self.numid)+">"
