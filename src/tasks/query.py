"""Tasks for CATCH searches."""
import os
import uuid

from catch import Catch, Config

from services.database_provider import db_engine_URI

CATCH_LOG: str = os.getenv('CATCH_LOG', default='/dev/null')


def catch_moving_target(desg: str, source: str, cached: bool, job_id: uuid.UUID) -> None:
    """Search for target in CATCH surveys.

    Parameters
    ----------
    desg : string
        Target designation.

    source : string
        Name of observation source to search or ``'any'``.

    cached : bool
        `True` to use cached results.

    job_id : uuid.UUID
        Unique ID for job.

    """

    config: Config = Config(database=db_engine_URI, log=CATCH_LOG)

    with Catch(config, save_log=True) as catch:
        catch.query(desg, job_id, source=source, cached=cached)
