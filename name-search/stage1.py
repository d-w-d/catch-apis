"""
STAGE 1 of Pipeline
Load search terms into DB
"""

import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, session as sqSession
from sqlalchemy.dialects.postgresql import insert, dml
from models.name_search import NameSearch, base
from env import ENV

# Import small body data output to csv file
dirname: str = os.path.dirname(os.path.realpath(__file__))
data_dir_path: str = dirname + '/mpcdata'
input_file: str = data_dir_path + "/minor_planets_names.csv"

name_search_items: List[NameSearch] = []
with open(input_file, encoding="utf-8") as content:
    lines = content.readlines()
    for line in lines:
        parts = line.split(',')
        try:
            name_search_items.append(
                NameSearch(
                    numid=int(parts[0].strip()),
                    accented=parts[1].strip(),
                    unaccented=parts[2].strip()
                )
            )
        except:
            # Header line will be rejected
            print('Rejected >>> '+str(parts))

# Build db-connection URI
db_engine_URI: str = (
    f"{ENV.DB_DIALECT}://{ENV.DB_USERNAME}:{ENV.DB_PASSWORD}@{ENV.DB_HOST}"
    f"/{ENV.DB_DATABASE}")
db: Engine = create_engine(db_engine_URI, pool_recycle=3600)

# Create tables if not exist
base.metadata.create_all(db)
# Create session
Session = sessionmaker(db)
session: sqSession.Session = Session()


if __name__ == "__main__":
    isUpserting = 0  # Toggle between upsert behavior and simple-upload
    for item in name_search_items:
        if isUpserting:
            # Use this for simple insertion; conflicts cause errors
            stmt: dml.Insert = insert(NameSearch).values(
                accented=item.accented,
                unaccented=item.unaccented,
                numid=item.numid
            )
            # Use this for updating on conflict
            stmt2: dml.Insert = stmt.on_conflict_do_update(
                constraint='small_bodies_pkey',  # Get this from `\d small_bodies;`
                set_=dict(
                    accented=item.accented,
                    unaccented=item.unaccented,
                )
            )
            # Use this for ignoring on conflict
            stmt3: dml.Insert = stmt.on_conflict_do_nothing()
            session.execute(stmt3)
        else:
            session.add(item)

    # Try committing changes; rollback on error
    try:
        session.commit()
    except:
        print("Egregious error invoked!")
        session.rollback()
