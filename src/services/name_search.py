"""Caught moving object data services."""

from typing import List
from .database_provider import data_provider_session, Session, db_engine
from models.small_body import base


# Create SmallBody table if not exists; make db aware of this model
base.metadata.create_all(db_engine)


def name_search(search_name: str) -> List:
    """
        XXX
    """
    found: List = []

    session: Session
    with data_provider_session() as session:
        q = session.execute(
            f"""
                SELECT unaccented, numid from (
                    SELECT *, getSearchText(small_bodies.*) as concat FROM small_bodies
                ) arbitrary_name
                ORDER BY (concat <-> '{search_name}')
                LIMIT 10;
            """

            # SELECT * from (
            #     SELECT *, getSearchText(small_bodies.*) as concat FROM small_bodies
            # ) yyy
            # -- WHERE concat % 'van gall'
            # ORDER BY (concat <-> 'van gall')
            # -- WHERE concat ILIKE '%van gaal%' -- Run this only when similarity is unavailable
            # LIMIT 10;


        )

        print("<><><><><>")
        for p in q:
            print(p)
            found.append(
                {
                    "unaccented": p[0],
                    "numid": p[1],
                }
            )

    return found
