"""
Catch a moving target in survey data.
"""

import os
from typing import List, Dict, Any
import uuid

from catch import Catch, Config
from catch.schema import CatchQueries, Caught, Found, Obs, Obj
from models.query import COLUMN_LABELS
from .database_provider import db_engine_URI, data_provider_session

CATCH_LOG: str = os.getenv('CATCH_LOG', default='/dev/null')
CONFIG: Config = Config(database=db_engine_URI, log=CATCH_LOG)


def query(target: str, job_id: uuid.UUID, source: str, cached: bool) -> List[Any]:
    """Run query and return caught data.


    Parameters
    ----------
    target : string
        Target for which to search.

    job_id : uuid.UUID
        Unique job ID.

    source : string
        Observation source.

    cached : bool
        OK to return cached results?


    Returns
    -------
    found : list
        Found observations and metadata.

    """
    with Catch(CONFIG, save_log=True) as catch:
        catch.query(target, job_id, source=source, cached=cached)

    found = caught(job_id)
    return found


def caught(job_id: uuid.UUID) -> List[dict]:
    """Caught object results.

    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.

    """

    with data_provider_session() as session:
        data = (session.query(Found, Obs, Obj)
                .join(Caught, Found.foundid == Caught.foundid)
                .join(CatchQueries, CatchQueries.queryid == Caught.queryid)
                .join(Obs, Found.obsid == Obs.obsid)
                .join(Obj, Found.objid == Obj.objid)
                .filter(CatchQueries.jobid == job_id.hex))
        session.expunge_all()

    # unpack into list of dictionaries for marshalling
    found: List[dict] = []
    for row in data:
        found.append(row._asdict())

        # some extras
        # rows[-1]['cutout_url'] = ...
        # rows[-1]['fullframe_url'] = ...

    return found


def check_cache(target: str, source: str) -> bool:
    """Check CATCH cache for previous query.


    Parameters
    ----------
    target : string
        Target name.

    source : string
        Observation source or ``'any'``.


    Returns
    -------
    cached : bool

        ``True`` if ``source`` has already been searched for
        ``target``.  When ``source`` is ``'any'``, then if any source
        was not searched, ``cached`` will be ``False``.

    """

    with Catch(CONFIG, save_log=False) as catch:
        cached = catch.check_cache(target, source=source)
    return cached


def column_labels(route: str) -> Dict[str, Dict[str, str]]:
    """Column labels for caught results."""
    return COLUMN_LABELS.get(route, {})
