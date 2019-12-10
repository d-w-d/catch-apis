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
                SELECT target_text, search_text, body_type FROM name_search
                ORDER BY (search_text <-> '{search_submission}')
                LIMIT 10;
            """
        )

        print("<><><><><>")
        for p in q:
            print(p)
            found.append(
                {
                    "target_text": p[0],
                    "body_type": p[1],
                }
            )

    return found
