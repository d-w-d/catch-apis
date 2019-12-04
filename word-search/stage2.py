"""
STAGE 2 of Pipeline
Build indexes, test uploads, etc.
"""

import time
from stage1 import session


# Create function to combine columns into one searchable piece of text
q = session.execute(
    """
        CREATE OR REPLACE FUNCTION getSearchText(small_bodies) RETURNS text AS $$
                        SELECT $1.unaccented || ' ' || $1.numid::text as concat;
        $$ LANGUAGE SQL;
        -- SELECT getSearchText(small_bodies.*) FROM small_bodies;
    """
)
session.commit()


# Create gin index; see not in readme
# Requires running `CREATE EXTENSION pg_trgm;`
# q = session.execute(
#     """
#         CREATE INDEX IF NOT EXISTS get_search_text_function_idx ON small_bodies USING gin(getSearchText(small_bodies.*) gin_trgm_ops);
#     """
# )
# session.commit()


# Test retrieval efficacy of search word
# Number of retrievals
retrievals: int = 1
# Mark start time
t1: float = time.time()
# Retrieve results multiple times for benchmarking
for i in list(range(0, retrievals)):
    q = session.execute(
        """
            SELECT * from (
                SELECT *, getSearchText(small_bodies.*) as concat FROM small_bodies
            ) yyy
            -- WHERE concat % 'van gall'
            ORDER BY (concat <-> 'van gall')
            -- WHERE concat ILIKE '%van gaal%' -- Run this only when similarity is unavailable
            LIMIT 10;
        """
    )

    # Print out retrieved data
    print("")
    for p in q:
        print(p)


print(f"time taken for {retrievals} retrievals:")
print(time.time() - t1)
