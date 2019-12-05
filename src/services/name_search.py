"""
    Caught moving object data services
"""

from typing import List
from .database_provider import data_provider_session, Session, db_engine
from models.name_search import base


# Create NameSearch table if not exists; make db aware of this model
base.metadata.create_all(db_engine)


def name_search(search_submission: str) -> List:
    """
        Function to query DB for matching names
    """
    found: List = []

    session: Session
    with data_provider_session() as session:
        q = session.execute(
            f"""
                SELECT unaccented, numid from (
                    SELECT *, getSearchText(small_bodies.*) as concat FROM small_bodies
                ) arbitrary_name
                ORDER BY (concat <-> '{search_submission}')
                LIMIT 10;
            """

            # SELECT * from (
            #     SELECT *, getSearchText(small_bodies.*) as concat FROM small_bodies
            # ) arbitrary_name
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
